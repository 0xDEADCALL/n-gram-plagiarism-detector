from PlagiarismDataHandler import *
from NGram import *
from DependencyRelations import *
from utils import *
if __name__ == '__main__':
    data = PlagiarismDataHandler("data/corpus/source-document", "data/corpus/suspicious-document")

    print(len(data.get_plagiarized_files()))
