# Imports
from pathlib import PurePath
from pathlib import Path
from errno import ENOENT
from os import strerror
from errors import *
from NGram import *
from random import sample
from multiprocessing import cpu_count

from istarmap import *
import xml.etree.ElementTree as ET
import tqdm
import shutil
import stanza


# TODO:
#   - Add proper documentation

# Worker functions, needs to be at the top to be pickled
def save_ngram_protected(path: pathlib.PurePath, output: pathlib.PurePath, order: int,
                         transformations: list = ["tok"]):
    NGram.from_txt_file(path, order, transformations).save(output / (path.stem + ".NGram"))


class PlagiarismFile:
    def __init__(self, xml_path: PurePath):
        self.xml_path = xml_path
        self.plagiarized_refs = None

        if not isinstance(xml_path, PurePath):
            raise NotPurePathError("xml arg is not PurePath object")

        if not xml_path.exists():
            raise FileNotFoundError(ENOENT, strerror(ENOENT), xml_path)

        self.plagiarized_refs = self.__process_xml()

    def __process_xml(self):
        xmlroot = ET.parse(self.xml_path).getroot()
        features = xmlroot.findall("feature[@name = 'plagiarism']")
        refs = []

        for feature in features:
            props = feature.attrib
            props["this_offset"] = int(props["this_offset"])
            props["this_length"] = int(props["this_length"])
            props["source_offset"] = int(props["source_offset"])
            props["this_length"] = int(props["this_length"])
            props["source_length"] = int(props["source_length"])
            props["source_file"] = props["source_reference"]

            del props["name"], props["this_language"], props["source_language"]
            refs.append(props)
        return refs

    def has_plagiarized_refs(self):
        return bool(self.plagiarized_refs)


class PlagiarismDataHandler:
    def __init__(self, root_source, root_suspicious):
        self.root_source = Path(root_source)
        self.root_suspicious = Path(root_suspicious)

        # Check if path exists, if not raise exception
        if not (self.root_source.exists() and self.root_source.is_dir()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), root_source)

        if not (self.root_suspicious.exists() and self.root_suspicious.is_dir()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), root_source)

        self.txt_source_paths, self.xml_source_paths = map(list, self.__get_source_paths())
        self.txt_suspicious_paths, self.xml_suspicious_paths = map(list, self.__get_suspicious_paths())

        self.plagiarized, self.non_plagiarized = self.rebuild_plagiarized()

    def __get_source_paths(self):
        txtfiles = self.root_source.glob("*.txt")
        xmlfiles = self.root_source.glob("*.xml")

        return txtfiles, xmlfiles

    def __get_suspicious_paths(self):
        txtfiles = self.root_suspicious.glob("*.txt")
        xmlfiles = self.root_suspicious.glob("*.xml")

        return txtfiles, xmlfiles

    def rebuild_files(self):
        self.txt_source_paths, self.xml_source_paths = map(list, self.__get_source_paths())
        self.txt_suspicious_paths, self.xml_suspicious_paths = map(list, self.__get_suspicious_paths())

    def rebuild_plagiarized(self):
        plagiarized = []
        non_plagiarized = []

        for sus_file in self.xml_suspicious_paths:
            ref = PlagiarismFile(sus_file)

            if ref.has_plagiarized_refs():
                plagiarized.append((sus_file.with_suffix(".txt"), ref))
            else:
                non_plagiarized.append(sus_file.with_suffix(".txt"))

        return plagiarized, non_plagiarized

    def build_subset(self, output: Path, total: int, plagiarized_percent: float, make_zip: False):
        # Let's classify first the docs
        source = []
        plagiarized = []
        n = round(total * plagiarized_percent)

        for file in sample(self.plagiarized, n):
            plagiarized.append(file[0])
            for ref in file[1].plagiarized_refs:
                sp = self.root_source / ref["source_file"]
                if sp not in source:
                    source.append(sp.with_suffix(".txt"))

        plagiarized += sample(self.non_plagiarized, total - n)
        if len(source) < total:
            source += sample(self.txt_source_paths, total - len(source))

        # Make subset folder
        output.mkdir(parents=True)
        source_path = (output / "source-document")
        source_path.mkdir(parents=True)
        suspicious_path = (output / "suspicious-document")
        suspicious_path.mkdir(parents=True)

        for f in tqdm.tqdm(source, desc="Copying source files..."):
            shutil.copy(f, source_path / f.name)
            shutil.copy(f.with_suffix(".xml"), source_path / (f.stem + ".xml"))

        for f in tqdm.tqdm(plagiarized, desc="Copying suspicious files..."):
            shutil.copy(f, suspicious_path / f.name)
            shutil.copy(f.with_suffix(".xml"), suspicious_path / (f.stem + ".xml"))

        if make_zip:
            print("Compressing files...")
            shutil.make_archive(output.stem, "zip", output)
            shutil.rmtree(Path(output))

    def gen_ngram_files(self, order: int, output: pathlib.PurePath, transformations: list = ["tok"]):

        if not isinstance(output, PurePath):
            raise NotPurePathError("output arg is not PurePath object")

        if not (output.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), output)

        # Make output dirs
        out_source = output / f"source-{order}-{'-'.join(transformations)}-ngram"
        out_suspicious = output / f"suspicious-{order}-{'-'.join(transformations)}-ngram"

        out_source.mkdir(parents=True, exist_ok=True)
        out_suspicious.mkdir(parents=True, exist_ok=True)

        source_files = self.txt_source_paths
        suspicious_files = self.txt_suspicious_paths

        args_source = list(zip(source_files,
                               [out_source] * len(source_files),
                               [order] * len(source_files),
                               [transformations] * len(source_files)))

        args_suspicious = list(zip(suspicious_files,
                                   [out_suspicious] * len(suspicious_files),
                                   [order] * len(suspicious_files),
                                   [transformations] * len(suspicious_files)))

        with mpp.Pool(cpu_count() + 2) as p:
            r = list(tqdm.tqdm(p.istarmap(save_ngram_protected, args_source),
                               total=len(args_source),
                               desc="Writing source .NGram files"))

        with mpp.Pool(cpu_count() + 2) as p:
            r = list(tqdm.tqdm(p.istarmap(save_ngram_protected, args_suspicious),
                               total=len(args_suspicious),
                               desc="Writing suspicious .NGram files"))
