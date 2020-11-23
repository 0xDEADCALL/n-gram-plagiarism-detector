from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from errors import UnknownOption


def preprocess(text: str, transformations: list = ["token"], lang: str = "english"):
    """
    Function used to preprocess a string before is converted into a feature.
    :param text: A string which will be processed.
    :param transformations: A list of strings containing the transformations to apply. The available strings are: ["stop",
    "lem", "alpha", "tok", "lower"].
    :param lang: A string, which language to use (important for lemmanization)
    :return: A list of processed tokens or a processed string
    """

    for opt in transformations:
        if opt not in ["stop", "tok", "lem", "lower", "alpha"]:
            raise UnknownOption(f"{opt} is not a known transformation")

    word_tokens = word_tokenize(text)
    # Remove stop words
    if "stop" in transformations:
        stop_words = set(stopwords.words(lang))
        word_tokens = [w for w in word_tokens if w not in stop_words]

    # Lemmatization of words
    if "lem" in transformations:
        lemmatizer = WordNetLemmatizer()
        word_tokens = [lemmatizer.lemmatize(w) for w in word_tokens]

    # Remove non-alphanumeric words
    if "alpha" in transformations:
        word_tokens = [w for w in word_tokens if w.isalpha()]

    # Tranform to lower
    if "lower" in transformations:
        word_tokens = [w.lower() for w in word_tokens]

    # Return tokenized
    if "tok" in transformations:
        return word_tokens
    else:
        return " ".join(word_tokens)
