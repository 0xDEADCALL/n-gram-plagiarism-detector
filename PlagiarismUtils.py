import argparse
import sys
import pickle
import pandas as pd
import numpy as np

from PlagiarismDataHandler import PlagiarismDataHandler
from BuildScoreCSV import writeCSV
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier


# TODO:
#   - Add documentation
#   - Add help string for commands

def dir_path(path):
    if Path(path).exists():
        return Path(path)
    else:
        raise argparse.ArgumentParser(f"{path} is not valid")


def out_path(path):
    if Path(path).parent.exists():
        return Path(path)
    else:
        raise argparse.ArgumentParser(f"{path} is not valid")


class PlagiarismUtils:
    def __init__(self):
        print("\n")
        parser = argparse.ArgumentParser(
            description="Utility app used to detect plagiarism and train it",
            usage=""" <command> [<args>]
            
            The available commands are:
                detect      Used to check if a given set has plagiarized instances
                subset      Used to generate a subset of files from a bigger one
                preprocess  Used to generate .dep and .NGram files
                scores      Used to generate a CSV file with the scores of set
            """
        )
        # Add subcommand arg
        parser.add_argument("command", help="Subcommand to run")
        # Parse the first arg -> subcommand
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print(f"{args.command} is no recognized command")
            parser.print_usage()
            exit(1)

        # Call subcommand routine
        getattr(self, args.command)()

    def subset(self):
        parser = argparse.ArgumentParser(
            description="Generate a subset from a larger one",
            usage="subset [src_files] [sus_files] [total] [prop (0 to 1)] [output_folder] [--zip]"
        )
        # Add args
        parser.add_argument("src_files", type=dir_path)
        parser.add_argument("sus_files", type=dir_path)
        parser.add_argument("total", type=int)
        parser.add_argument("prop", type=float)
        parser.add_argument("output_name", type=out_path)
        parser.add_argument("--zip", action="store_true")

        # Parse args
        args = parser.parse_args(sys.argv[2:])

        handler = PlagiarismDataHandler(args.src_files, args.sus_files)
        handler.build_subset(args.output_name, args.total, args.prop, args.zip)

    def preprocess(self):
        parser = argparse.ArgumentParser(
            description="Generate preprocessed features (ngrams and syntactic dependency relations) used to detection",
            usage="""preprocess [src_files] [sus_files] [output_folder] [order] [opts (tok, lem, lower, alpha)]"""
        )

        # Add args
        parser.add_argument("src_files", type=dir_path)
        parser.add_argument("sus_files", type=dir_path)
        parser.add_argument("output", type=dir_path)
        parser.add_argument("order", type=int, default=3)
        parser.add_argument("opts", nargs="*")

        # Parse args
        args = parser.parse_args(sys.argv[2:])

        handler = PlagiarismDataHandler(args.src_files, args.sus_files)
        
        if args.opts:
            handler.gen_ngram_files(args.order, args.output, args.opts)
        else:
            raise argparse.ArgumentParser(f"A set of transformations need to be specified")

    def scores(self):
        parser = argparse.ArgumentParser(
            description="Generate .csv file with the similarity scores for every preprocessed feature",
            usage="""scores [src_files] [sus_files] [feature_files_folder] [output] [--train]"""
        )

        # Add args
        parser.add_argument("src_files", type=dir_path)
        parser.add_argument("sus_files", type=dir_path)
        parser.add_argument("feature_files", type=dir_path)
        parser.add_argument("output", type=out_path)
        parser.add_argument("--train", action="store_true")

        # Parse args
        args = parser.parse_args(sys.argv[2:])

        # Write a the CSV
        writeCSV(args.feature_files,
                 list(args.src_files.glob("*.txt")),
                 list(args.sus_files.glob("*.txt")),
                 args.output,
                 is_training=args.train)

    def detect(self):
        parser = argparse.ArgumentParser(
            description="Detect plagiarized instances in a given set"
        )

        # Add parser
        parser.add_argument("scores", type=dir_path)
        parser.add_argument("model", type=dir_path)
        parser.add_argument("output", type=out_path)

        # Parse args
        args = parser.parse_args(sys.argv[2:])

        # Load model and make it predict
        with open(args.model, "rb") as f:
            tree = pickle.load(f)
        data = pd.read_csv(args.scores, header=0)

        X = data.drop(["src", "sus", "plagiarized"], axis=1, errors="ignore")

        if len(tree.feature_importances_) != len(X.columns):
            raise argparse.ArgumentParser(f"Model features don't match with the .csv vars number")

        y = tree.predict(X)
        idx = np.where(y == 1)

        res = data.iloc[idx][["src", "sus"]]
        res["prob"] = tree.predict_proba(X)[idx][:, 1]

        res.to_csv(args.output, index=False)


# Entry point
if __name__ == "__main__":
    PlagiarismUtils()
