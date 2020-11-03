from DataHandler import *
from NGram import *
from DependencyRelations import *

data = DataHandler("data/corpus/source-document", "data/corpus/suspicious-document")
SS = list(data.get_suspicious_fnames()[0])[6]
SO = list(data.get_source_fnames()[0])[0]


DSS = DependencyRelations(file_path=SS)
DSO = DependencyRelations(file_path=SO)

print(DSS.similarity(DSO))

