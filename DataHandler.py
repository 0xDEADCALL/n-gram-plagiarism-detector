# Imports
from pathlib import Path
from errno import ENOENT
from os import strerror

import xml.etree.ElementTree as ET


# Class that simplifies the handling of the corpus
# text in the data files
class DataHandler:
    # Args:
    #   root: filepath of the corpus data
    # Returns:
    #   dataHandler object
    def __init__(self, root_source, root_suspicious):
        self.root_source = Path(root_source)
        self.root_suspicious = Path(root_suspicious)

        # Check if path exists, if not raise exception
        if not (self.root_source.exists() and self.root_source.is_dir()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), root_source)

        if not (self.root_suspicious.exists() and self.root_suspicious.is_dir()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), root_source)

    # Args:
    #   None
    # Returns:
    #   Tuples with lists of ".txt" and ".xml" source paths
    def get_source_fnames(self):
        txtfiles = self.root_source.glob("*.txt")
        xmlfiles = self.root_source.glob("*.xml")

        return txtfiles, xmlfiles

    # Args:
    #   None
    # Returns:
    #   Tuples with lists of ".txt" and ".xml" suspicous paths
    def get_suspicious_fnames(self):
        txtfiles = self.root_suspicious.glob("*.txt")
        xmlfiles = self.root_suspicious.glob("*.xml")

        return txtfiles, xmlfiles

    # Args:
    #   xmlpath: XML filepath
    # Returns:
    #   Dict with the plagiarism references
    def get_plagiarism_refs(self, xmlpath):
        xmlroot = ET.parse(xmlpath).getroot()
        features = xmlroot.findall("feature[@name = 'plagiarism']")

        return [feature.attrib for feature in features]






