# Imports
import pathlib

from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from errors import *
from errno import ENOENT
from os import strerror


# TODO:
#   - Add proper documentation to methods
class NGram:
    def __init__(self, ngram_list: list, order: int):
        self.order = order
        self.__list = ngram_list

    def __repr__(self):
        head = "\n".join(str(x) for x in self.__list[:5])
        return "NGram object of order {}\nHead:\n{}\n ...".format(self.order, head)

    def __getitem__(self, item):
        return self.__list[item]

    def __iter__(self):
        return iter(self.__list)

    @classmethod
    def from_txt_file(cls, file_path: pathlib.PurePath, order: int):
        # Check if we have a PurePath object
        if not isinstance(file_path, pathlib.PurePath):
            raise NotPurePathError

        # Check if path exists, if not raise exception
        if not (file_path.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

        with open(file_path, "r", encoding="utf-8-sig") as f:
            return cls(list(ngrams(word_tokenize(f.read()), order)), order)

    @classmethod
    def from_ngram_file(cls, file_path: pathlib.PurePath):
        # Check if we have a PurePath object
        if not isinstance(file_path, pathlib.PurePath):
            raise NotPurePathError

        # Check if path exists, if not raise exception
        if not (file_path.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

        with open(file_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            return cls([tuple(line.rstrip().split("~")) for line in lines[1:]], int(lines[0]))

    @classmethod
    def from_str(cls, text_str: str, order: int):
        return cls(list(ngrams(word_tokenize(text_str), order)), order)

    def similarity(self, ngram, coef_type: str = "jaccard"):
        if coef_type not in ["jaccard", "containment"]:
            raise NGramUnknownCoefficient

        # Add some clarity and avoid recomputing sets
        a = set(self.__list)
        b = set(list(ngram))
        aintb = a & b

        if coef_type == "jaccard":
            return len(aintb) / len(a | b)
        else:
            return len(aintb) / len(a)

    def save(self, file_path: pathlib.PurePath):
        # Check if we have a PurePath object
        if not isinstance(file_path, pathlib.PurePath):
            raise NotPurePathError

        with open(file_path, "w", encoding="utf-8-sig") as f:
            f.write(str(self.order) + "\n")
            f.write("\n".join(["~".join(x) for x in self.__list]))
