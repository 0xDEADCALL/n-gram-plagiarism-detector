from DataHandler import *
from NGram import *

data = DataHandler("data/corpus/source-document", "data/corpus/suspicious-document")
fnames = list(list(data.get_suspicious_fnames())[0])
ngram = get_ngram(fnames[0], 2, True)

print(list(ngram))
