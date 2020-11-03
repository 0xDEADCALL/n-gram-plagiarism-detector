# Imports
import pathlib

from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from errors import *
from errno import ENOENT
from os import strerror

# TODO:
#   - Add header to ngram file
#   - Add methods to compare sets of ngrams

class NGram:
    def __init__(self, filepath, isngram = False, order = None):
        # Check if we have a PurePath object
        if not isinstance(filepath, pathlib.PurePath):
            raise NotPurePathError

        # Check if path exists, if not raise exception
        if not (self.filepath.exists()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), filepath)

        # Save filepath
        self.filepath = filepath

        # Check method of loading and if order is specified
        if isngram is False:
            if order is None:
                raise NGramOrderNotSpecified
            else:
                self.order = order
                self.__list = self.__gen_from_txt()
        else:
            self.__list = self.__gen_from_ngram()
            self.order =





        self.order = order

    def __gen_from_txt(self):
        with open(self.filepath, "r", encoding="utf-8-sig") as f:
            ngram = list(ngrams(word_tokenize(f.read()), self.order))
            return ngram

    def __gen_from_ngram(self):
        with open(self.filepath, "r", encoding="utf-8-sig") as f:
            ngram = [tuple(line.split("~")) for line in f.readlines()]
            return ngram


    def save(self):
        dest = self.filepath.parents[0] / "{}.NGram".format(self.filepath.stem)
        with open(dest, "w", encoding="utf-8-sig") as f:
            f.write("\n".join(["~".join(x) for x in self.__list]))

