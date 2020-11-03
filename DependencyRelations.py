import pathlib

from collections import Counter
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.tokenize import sent_tokenize
from errors import *
from errno import ENOENT
from os import strerror


class DependencyRelations:
    # Inits a Dependency object
    # Args:
    #   text_str: A string to tranform in NGrams
    #   filepath: pathlib object that points to a .txt file is located
    #   is_dep: bool that specifies if a txt or a .dep file is loaded
    # Returns:
    #   Nothing
    def __init__(self, file_path: pathlib.PurePath = None, text_str: str = None,
                 is_dep: bool = False):
        # Default vars
        self.__str = text_str
        self.file_path = file_path

        if file_path is not None:
            # Check if we have a PurePath object
            if not isinstance(file_path, pathlib.PurePath):
                raise NotPurePathError

            # Check if path exists, if not raise exception
            if not (file_path.exists()):
                raise FileNotFoundError(ENOENT, strerror(ENOENT), file_path)

            # Check method of loading and if order is specified
            if is_dep is False:
                self.__list = self.__gen_from_txt()
            else:
                self.__list = self.__gen_from_dep()

        elif text_str is not None:
            self.__list = self.__gen_from_str(self.__str)
        else:
            raise DepRelNoInput

    def __repr__(self):
        head = "\n".join(str(x) for x in self.__list[:5])
        return "DependecyRelations\nHead:\n{}\n ...".format(head)

    def __getitem__(self, item):
        return self.__list[item]

    def __iter__(self):
        return iter(self.__list)

    # Generates dependency relations from txt files
    # Args:
    #   None
    # Returns:
    #   list of dependency relations as tuples
    def __gen_from_txt(self):
        with open(self.file_path, "r", encoding="utf-8-sig") as f:
            return self.__gen_from_str(f.read())

    # Initializes a DependencyRelations object from previosly saved .dep file
    # Args:
    #   None
    # Returns:
    #   list of dependency relations as tuples
    def __gen_from_dep(self):
        with open(self.file_path, "r", encoding="utf-8-sig") as f:
            dependencies = [tuple(line.rstrip().split("~")) for line in f.readlines()]
            return dependencies

    # Generates dependency relations from a str
    # Args:
    #   None
    # Returns:
    #   list of dependency relations as tuples
    def __gen_from_str(self, text):
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

    def save(self, alt_path: pathlib.PurePath = None):
        if alt_path is None and self.file_path is None:
            raise PathNotSpecified

        path = self.file_path.with_suffix(".dep") if alt_path is None else alt_path
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("\n".join(["~".join(x) for x in self.__list]))

    def similarity(self, dep):
        a = Counter(self.__list)
        b = Counter(list(dep))

        return len(a & b) / len(a)

