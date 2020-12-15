from PlagiarismDataHandler import *
from NGram import *
from DependencyRelations import *
from utils import *

if __name__ == '__main__':
    # data = PlagiarismDataHandler("data/corpus/source-document", "data/corpus/suspicious-document")
    # data.build_subset(500, 0.5)

    subdata = PlagiarismDataHandler("subset/source-document", "subset/suspicious-document")
    subdata.gen_ngram_files(3, Path("subset"),)
    #subdata.gen_dep_files(Path("subset"))


