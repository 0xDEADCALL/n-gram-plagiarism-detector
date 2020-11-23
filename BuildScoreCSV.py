from pathlib import Path, PurePath
from NGram import *
from DependencyRelations import *
from errors import *
from istarmap import *
from multiprocessing import Manager, Pool, cpu_count
from tqdm import tqdm
from PlagiarismDataHandler import PlagiarismFile


def __get_tmp_folders(tmp_folder):
    """
    Private function used to gather the names of the preprocessed features folders
    :param tmp_folder: A Path object with the path of the preprocessed folder's features.
    :return: A dictionary containing the name of the feature as the key and the
    his folder's path as the value.
    """
    # Check if a Path object is passed
    if not isinstance(tmp_folder, PurePath):
        raise NotPurePathError("tmp_folder arg is not PurePath object")

    # Get the corresponding folders
    # They must have the same order
    src_ngrams = list(tmp_folder.glob("source-*-ngram"))
    sus_ngrams = list(tmp_folder.glob("suspicious-*-ngram"))
    src_dep = list(tmp_folder.glob("source-dep"))
    sus_dep = list(tmp_folder.glob("suspicious-dep"))

    if len(src_ngrams) != len(sus_ngrams):
        raise TmpDirectoryError

    # Classify ngram types and dep types
    processed = {}
    for src_ngram, sus_ngram in zip(src_ngrams, sus_ngrams):
        processed[src_ngram.stem.replace("source-", "")] = (src_ngram, sus_ngram)

    if src_dep and sus_dep:
        processed["dep"] = (src_dep[0], sus_dep[0])

    return processed


def __write(q, output, header):
    """
    Private worker function used to write the distances
    to the output files.
    :param q: Manager().Queue() object
    :param output: Path object where the output file will be located
    :param header: List of strings containing the name for every var in the CSV
    :return: Nothing
    """

    if not isinstance(output, PurePath):
        raise NotPurePathError("output arg is not PurePath object")

    with open(output, "a+") as f:
        f.write(",".join(header) + "\n")
        while True:
            m = q.get()

            if m == "kill":
                break

            f.write(",".join([str(x) for x in list(m.values())]) + "\n")
            f.flush()


def __calc_distance(q, pair, is_training=False):
    """
    Private function used to calculate the preprocessed features similarities in bulk.
    :param q: Manager().Queue() object
    :param pair: A dict containing the the paths of the src and sus files as well as his preprocessed features.
    :param is_training: A bool indicating if the CSV formed is for training a model, the corresponding .xml file
    must be in the same folder as the sus file.
    :return: a dict containing the similarity for every feature.
    """
    distances = {"src": pair["src"].name, "sus": pair["sus"].name}

    for key, value in list(pair.items())[2:]:
        src = value[0]
        sus = value[1]

        if key == "dep":
            src_dep = DependencyRelations.from_dep_file(src)
            sus_dep = DependencyRelations.from_dep_file(sus)
            distances[key] = sus_dep.similarity(src_dep)

        else:
            src_ngram = NGram.from_ngram_file(src)
            sus_ngram = NGram.from_ngram_file(sus)
            distances[key] = sus_ngram.similarity(src_ngram)

    if is_training:
        src_refs = [xml["source_file"] for xml in PlagiarismFile(pair["sus"].with_suffix(".xml")).plagiarized_refs]
        distances["plagiarized"] = 1 if pair["src"].name in src_refs else 0

    q.put(distances)
    return distances


def writeCSV(tmp_folder, src_files, sus_files, output, is_training=False):
    """
    Functions used to generate as CSV with the similarity scores between a set of src and sus documents.
    :param tmp_folder: A Path object containing the folder where the preprocessed features are located
    :param src_files: A Path object containing the folder where the source files are located.
    :param sus_files: A Path object containing the folder where de suspicious files are located.
    :param output: A path object containing the CSV output location
    :param is_training: A bool indicating if the CSV is for training (a columns indicating if its plagiarized will be
    added). The corresponding .xml files must be in the same folder as the sus files.
    :return: Nothing
    """
    # Def queue and pool with saturated threads
    manager = Manager()
    q = manager.Queue()
    pool = mpp.Pool(cpu_count() + 2)

    # Make list of pairs
    pairs = []
    folders = __get_tmp_folders(tmp_folder)
    for sus in sus_files:
        for src in src_files:
            pairs.append({"sus": sus, "src": src})
            for key, value in folders.items():
                suffix = ".dep" if key == "dep" else ".NGram"
                pairs[-1][key] = (value[0] / (src.stem + suffix),
                                  value[1] / (sus.stem + suffix))

    # Def header to identify scores
    header = ["src", "sus"] + list(folders.keys())
    if is_training:
        header += ["plagiarized"]

    # Start listener
    receiver = pool.apply_async(__write, (q, output, header))

    # Start workers
    args = list(zip([q] * len(pairs), pairs, [is_training] * len(pairs)))
    workers = list(tqdm(pool.istarmap(__calc_distance, args),
                        total=len(args),
                        desc="Calculating distances..."))

    # Break condition
    q.put("kill")
    pool.close()
    pool.join()
