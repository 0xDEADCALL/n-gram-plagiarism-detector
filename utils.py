import subprocess
from pathlib import PurePath, Path
from errors import *
from errno import ENOENT
from os import strerror
from time import sleep


def launch_corenlp_server(corenlp_folder: PurePath):
    if not isinstance(corenlp_folder, PurePath):
        raise NotPurePathError("coreNLP_folder arg is not PurePath object")

    if not (corenlp_folder.exists()):
        raise FileNotFoundError(ENOENT, strerror(ENOENT), corenlp_folder)

    command = '''java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \\ 
             -preload tokenize,ssplit,pos,depparse \\ 
             -status_port 9000 -port 9000 -timeout 15000 -quiet True & '''

    try:
        subprocess.Popen(command, cwd=corenlp_folder, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except subprocess.CalledProcessError:
        print("Couln't start coreNLP server")

    # Wait until coreNLP started
    sleep(30)

