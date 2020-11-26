from nltk.util import everygrams


class NaiveTokenizer:
    def tokenize(self, string):
        """Breaks string into lowercase word tokens."""
        return iter(string.strip().lower().split())


class NgramTokenizer:
    def __init__(self, tokenizer=NaiveTokenizer(), max_len=3):
        self.tokenizer = tokenizer
        self.max_len = max_len

    def tokenize(self, text):
        for ngram in everygrams(
            tuple(self.tokenizer.tokenize(text)), max_len=self.max_len
        ):
            yield " ".join(ngram)
