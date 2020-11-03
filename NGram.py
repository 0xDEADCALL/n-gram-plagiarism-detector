# Imports
import pathlib

from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from errors import *
from errno import ENOENT
from os import strerror

# TODO:
#   - Make some base class to tidy code
#   - Fix __gen_from_str to be reusable by the other functions
#   - Find a better way to deal with multiple input ways

class NGram:
    # Inits a ngram object
    # Args:
    #   text_str: A string to tranform in NGrams
    #   filepath: pathlib object that points to a .txt file is located
    #   isngram: bool that speciefies if a txt or a ngram file is loaded
    #   order: order of the ngram to generate, 2 -> bigram, 3 -> trigram...
    # Return:
    #   Nothing
    def __init__(self, file_path: pathlib.PurePath = None, text_str: str = None,
                 is_ngram: bool = False, order: int = None):
        # Default vars
        self.file_path = file_path

        if file_path is not None:
            # Check if we have a PurePath object
            if not isinstance(file_path, pathlib.PurePath):
                raise NotPurePathError

            # Check if path exists, if not raise exception
            if not (file_path.exists()):
                raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

            # Check method of loading and if order is specified
            if is_ngram is False:
                if type(order) != int or order < 0:
                    raise NGramOrderNotSpecified
                else:
                    self.order = order
                    self.__list = self.__gen_from_txt()
            else:
                self.__list = self.__gen_from_ngram()

        elif text_str is not None:
            if type(order) != int or order < 0:
                raise NGramOrderNotSpecified

            self.order = order
            self.__list = self.__gen_from_str(text_str)
        else:
            raise NGramNoInput

    def __repr__(self):
        head = "\n".join(str(x) for x in self.__list[:5])
        return "NGram object of order {}\nHead:\n{}\n ...".format(self.order, head)

    def __getitem__(self, item):
        return self.__list[item]

    def __iter__(self):
        return iter(self.__list)

    # Generates ngrams from a txt files
    # Args:
    #   None
    # Returns:
    #   list of ngrams as tuples
    def __gen_from_txt(self):
        with open(self.file_path, "r", encoding="utf-8-sig") as f:
            return self.__gen_from_str(f.read())

    # Initializes a NGram object from previosly saved .NGram file
    # Args:
    #   None
    # Returns:
    #   list of ngrams as tuples
    def __gen_from_ngram(self):
        with open(self.file_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

            self.order = int(lines[0])
            ngram = [tuple(line.rstrip().split("~")) for line in lines[1:]]
            return ngram

    # Generates ngrams from a str
    # Args:
    #   None
    # Returns:
    #   list of ngrams as tuples
    def __gen_from_str(self, text):
        return list(ngrams(word_tokenize(text), self.order))

    # Computes the similarity between two NGrams using multiple coefficients
    # Args:
    #   ngram: Another NGram object against which the similarity will be computed
    # Returns:
    #   float: a similarity coefficient
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

    # Saves the current instance of a NGram object into a file in the same directory as the base .txt file or in
    # altpath
    # Args:
    #   altpath: Alternative file path where the .NGram file will be saved, must be specified if generated from string
    # Returns:
    #   Nothing
    def save(self, alt_path: pathlib.PurePath = None):
        if alt_path is None and self.file_path is None:
            raise PathNotSpecified

        path = self.file_path.with_suffix(".NGram") if alt_path is None else alt_path
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write(str(self.order) + "\n")
            f.write("\n".join(["~".join(x) for x in self.__list]))


