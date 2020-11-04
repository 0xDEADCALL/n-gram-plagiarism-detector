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


# TODO:
#   - Add proper documentation

# Worker functions, needs to be at the top to be pickled
def save_ngram_protected(path: pathlib.PurePath, order: int, force_rewrite=True):
    if path.exists():
        if force_rewrite:
            NGram.from_txt_file(path, order).save(path.with_suffix(".NGram"))
    else:
        NGram.from_txt_file(path, order).save(path.with_suffix(".NGram"))


def save_dep_protected(path: pathlib.PurePath, force_rewrite=True):
    if path.exists():
        if force_rewrite:
            DependencyRelations.from_txt_file(path).save(path.with_suffix(".dep"))
    else:
        DependencyRelations.from_txt_file(path).save(path.with_suffix(".dep"))


class PlagiarismFile:
    def __init__(self, nid: int, file_path: PurePath, xml_path: PurePath = None):
        # Raise appropriate expcetion if there is any problem with the paths
        if not isinstance(file_path, PurePath):
            raise NotPurePathError("basefile arg is not PurePath object")

        if not (file_path.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

        self.nid = nid
        self.file_path = file_path
        self.xml_path = xml_path
        self.plagiarized_refs = None

        if xml_path is not None:
            if not isinstance(xml_path, PurePath):
                raise NotPurePathError("xml arg is not PurePath object")

            if not (xml_path.exists()):
                raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

            self.xml_path = xml_path
            self.plagiarized_refs = self.__process_xml()

    def __process_xml(self):
        xmlroot = ET.parse(self.xml).getroot()
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
        self.txt_suspicious_paths, self.xml_suspicious_paths = map(list, self.__get_source_paths())

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
        self.txt_suspicious_paths, self.xml_suspicious_paths = map(list, self.__get_source_paths())

    def gen_ngram_files(self, order: int, threads: int = 1, force_rewrite=True,
                        verbose=True, max_source=None, max_suspicious=None):

        files = self.txt_source_paths[:max_source] + self.txt_suspicious_paths[:max_suspicious]
        args = list(zip(files, [order] * len(files), [force_rewrite] * len(files)))

        with mpp.Pool(threads) as p:
            r = list(tqdm.tqdm(p.istarmap(save_ngram_protected, args), total=len(args), disable=not verbose))

    def gen_dep_files(self, threads: int = 1, force_rewrite=True,
                      verbose=True, max_source=None, max_suspicious=None):

        files = self.txt_source_paths[:max_source] + self.txt_suspicious_paths[:max_suspicious]
        args = list(zip(files, [force_rewrite] * len(files)))

        with mpp.Pool(threads) as p:
            r = list(tqdm.tqdm(p.istarmap(save_dep_protected, args), total=len(args), disable=not verbose))
