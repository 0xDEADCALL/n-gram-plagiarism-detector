# Imports
from pathlib import PurePath
from pathlib import Path
from errno import ENOENT
from os import strerror
from errors import *
from NGram import *
from DependencyRelations import *

from istarmap import *
import xml.etree.ElementTree as ET
import tqdm
import shutil


# TODO:
#   - Add proper documentation

# Worker functions, needs to be at the top to be pickled
def save_ngram_protected(path: pathlib.PurePath, output: pathlib.PurePath, order: int, force_rewrite=True):
    if path.exists():
        if force_rewrite:
            NGram.from_txt_file(path, order).save(output / (path.stem + ".NGram"))
    else:
        NGram.from_txt_file(path, order).save(output / (path.stem + ".NGram"))


def save_dep_protected(path: pathlib.PurePath, output: pathlib.PurePath, force_rewrite=True):
    if path.exists():
        if force_rewrite:
            DependencyRelations.from_txt_file(path).save(output / (path.stem + ".dep"))
    else:
        DependencyRelations.from_txt_file(path).save(output / (path.stem + ".dep"))


class PlagiarismFile:
    def __init__(self, xml_path: PurePath = None):
        self.xml_path = xml_path
        self.plagiarized_refs = None

        if xml_path is not None:
            if not isinstance(xml_path, PurePath):
                raise NotPurePathError("xml arg is not PurePath object")

            if not (xml_path.exists()):
                raise FileNotFoundError(ENOENT, strerror(ENOENT), xml_path)

            self.xml_path = xml_path
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

    def __get_source_paths(self):
        txtfiles = self.root_source.glob("*.txt")
        xmlfiles = self.root_source.glob("*.xml")

        return txtfiles, xmlfiles

    def __get_suspicious_paths(self):
        txtfiles = self.root_suspicious.glob("*.txt")
        xmlfiles = self.root_suspicious.glob("*.xml")

        return txtfiles, xmlfiles

    def rebuild(self):
        self.txt_source_paths, self.xml_source_paths = map(list, self.__get_source_paths())
        self.txt_suspicious_paths, self.xml_suspicious_paths = map(list, self.__get_suspicious_paths())

    def build_subset(self, total: int, max_plagiarized: int):
        # Let's classify first the docs
        plagiarized = []
        nonplagiarized = []
        source = []

        for sus_file in self.xml_suspicious_paths:
            ref = PlagiarismFile(sus_file)

            if ref.has_plagiarized_refs():
                plagiarized.append((sus_file, ref))
            else:
                nonplagiarized.append(sus_file)





    def gen_ngram_files(self, order: int, output: pathlib.PurePath, threads: int = 1, force_rewrite=True,
                        verbose=True, max_source=None, max_suspicious=None):

        if not isinstance(output, PurePath):
            raise NotPurePathError("output arg is not PurePath object")

        if not (output.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), output)

        # Make output dirs
        out_source = output / f"source-{order}-ngram"
        out_suspicious = output / f"suspicious-{order}-ngram"

        out_source.mkdir(parents=True, exist_ok=True)
        out_suspicious.mkdir(parents=True, exist_ok=True)

        source_files = self.txt_source_paths[:max_source]
        suspicious_files = self.txt_suspicious_paths[:max_suspicious]

        args_source = list(zip(source_files,
                               [out_source] * len(source_files),
                               [order] * len(source_files),
                               [force_rewrite] * len(source_files)))

        args_suspicious = list(zip(suspicious_files,
                                   [out_suspicious] * len(suspicious_files),
                                   [order] * len(suspicious_files),
                                   [force_rewrite] * len(suspicious_files)))

        with mpp.Pool(threads) as p:
            r = list(tqdm.tqdm(p.istarmap(save_ngram_protected, args_source),
                               total=len(args_source),
                               disable=not verbose,
                               desc="Writing source .NGram files"))

        with mpp.Pool(threads) as p:
            r = list(tqdm.tqdm(p.istarmap(save_ngram_protected, args_suspicious),
                               total=len(args_suspicious),
                               disable=not verbose,
                               desc="Writing suspicious .NGram files"))
    """
    def gen_dep_files(self, output: pathlib.PurePath, threads: int = 1, force_rewrite=True,
                      verbose=True, max_source=None, max_suspicious=None):

        if not isinstance(output, PurePath):
            raise NotPurePathError("output arg is not PurePath object")

        if not (output.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), output)

        # Make output dirs
        out_source = output / f"source-dep"
        out_suspicious = output / f"suspicious-dep"

        out_source.mkdir(parents=True, exist_ok=True)
        out_suspicious.mkdir(parents=True, exist_ok=True)

        source_files = self.txt_source_paths[:max_source]
        suspicious_files = self.txt_suspicious_paths[:max_suspicious]

        args_source = list(zip(source_files,
                               [out_source] * len(source_files),
                               [force_rewrite] * len(source_files)))

        # Complete with stanza
        """