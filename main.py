from PlagiarismDataHandler import *
from NGram import *
from DependencyRelations import *
from utils import *
if __name__ == '__main__':
    launch_corenlp_server(Path("stanford-corenlp-4.1.0"))

    data = PlagiarismDataHandler("data/corpus/source-document", "data/corpus/suspicious-document")
    data.gen_dep_files(threads=6, max_source=100, max_suspicious=100)