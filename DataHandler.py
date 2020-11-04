# Imports
from pathlib import Path
from errno import ENOENT
from os import strerror

import xml.etree.ElementTree as ET


# TODO:
#   - Add proper documentation
#   - Format dictionary attribs
#   - Add ID system

class DataHandler:
    def __init__(self, root_source, root_suspicious):
        self.root_source = Path(root_source)
        self.root_suspicious = Path(root_suspicious)

        # Check if path exists, if not raise exception
        if not (self.root_source.exists() and self.root_source.is_dir()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), root_source)

        if not (self.root_suspicious.exists() and self.root_suspicious.is_dir()):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), root_source)

    def get_source_fnames(self):
        txtfiles = self.root_source.glob("*.txt")
        xmlfiles = self.root_source.glob("*.xml")

        return txtfiles, xmlfiles

    def get_suspicious_fnames(self):
        txtfiles = self.root_suspicious.glob("*.txt")
        xmlfiles = self.root_suspicious.glob("*.xml")

        return txtfiles, xmlfiles

    def get_plagiarism_refs(self, xmlpath):
        xmlroot = ET.parse(xmlpath).getroot()
        features = xmlroot.findall("feature[@name = 'plagiarism']")

        return [feature.attrib for feature in features]
