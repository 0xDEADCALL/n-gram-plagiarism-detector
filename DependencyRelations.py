import pathlib

from collections import Counter
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.tokenize import sent_tokenize
from errors import *
from errno import ENOENT
from os import strerror


# TODO:
#   - Add proper documentation to methods

def _dep_rel_as_list(text):
    try:
        parser = CoreNLPDependencyParser(url="http://localhost:9000")
    except:  # Need to add de correct exceptions
        print("Is CoreNLP running???")
        return

    sentences = sent_tokenize(text)
    dependencies = []

    for sentence in sentences:
        parsed = parser.raw_parse(sentence)
        for y in [list(x.triples()) for x in parsed]:
            for gov, dep, dependent in y:
                dependencies.append((dep, gov[0], dependent[0]))

    return dependencies


class DependencyRelations:
    def __init__(self, dep_list: list):
        self.__list = dep_list

    def __repr__(self):
        head = "\n".join(str(x) for x in self.__list[:5])
        return "DependecyRelations\nHead:\n{}\n ...".format(head)

    def __getitem__(self, item):
        return self.__list[item]

    def __iter__(self):
        return iter(self.__list)

    @classmethod
    def from_txt_file(cls, file_path: pathlib.PurePath):
        # Check if we have a PurePath object
        if not isinstance(file_path, pathlib.PurePath):
            raise NotPurePathError

        # Check if path exists, if not raise exception
        if not (file_path.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

        with open(file_path, "r", encoding="utf-8-sig") as f:
            return cls(_dep_rel_as_list(f.read()))

    @classmethod
    def from_dep_file(cls, file_path: pathlib.PurePath):
        # Check if we have a PurePath object
        if not isinstance(file_path, pathlib.PurePath):
            raise NotPurePathError

        # Check if path exists, if not raise exception
        if not (file_path.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

        with open(file_path, "r", encoding="utf-8-sig") as f:
            return cls([tuple(line.rstrip().split("~")) for line in f.readlines()])

    @classmethod
    def from_str(cls, text_str: str):
        return cls(_dep_rel_as_list(text_str))

    def save(self, file_path: pathlib.PurePath):
        # Check if we have a PurePath object
        if not isinstance(file_path, pathlib.PurePath):
            raise NotPurePathError

        with open(file_path, "w", encoding="utf-8-sig") as f:
            f.write("\n".join(["~".join(x) for x in self.__list]))

    def similarity(self, dep):
        a = Counter(self.__list)
        b = Counter(list(dep))

        return len(a & b) / len(a)
