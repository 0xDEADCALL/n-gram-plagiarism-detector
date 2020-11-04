from DataHandler import *
from NGram import *
from DependencyRelations import *

data = DataHandler("data/corpus/source-document", "data/corpus/suspicious-document")
txt_source, xml_source = list(data.get_source_fnames())
txt_susp, xml_susp = list(data.get_suspicious_fnames())

f = list(xml_susp)[6]
print(f)
print(data.get_plagiarism_refs(f))
