import string
import time
from collections import Counter

from columnar import columnar
from pympler.asizeof import asizeof
from nltk.corpus import gutenberg
from nltk.util import everygrams
from nltk.collocations import (
    BigramAssocMeasures,
    BigramCollocationFinder,
    TrigramAssocMeasures,
    TrigramCollocationFinder,
)


from ..matchers import benchmark_algolist


def clean_text(corpus):
    table = str.maketrans("", "", string.punctuation)
    return corpus.translate(table).lower()


def find_nbest(measures, finder, words, n):
    measures = measures()
    finder = finder.from_words(words)
    return [" ".join(ngram) for ngram in finder.nbest(measures.pmi, n)]


def find_nbest_unigrams(words, n):
    counter = Counter((word for word in words))
    return [word for word, _ in counter.most_common(n)]


def find_top_ngrams(words, n):
    top_trigrams = find_nbest(TrigramAssocMeasures, TrigramCollocationFinder, words, n)

    top_bigrams_in_trigrams = []
    for trigram in top_trigrams:
        for bigram in everygrams(trigram.split(), min_len=2, max_len=2):
            top_bigrams_in_trigrams.append(" ".join(bigram))

    top_bigrams = find_nbest(BigramAssocMeasures, BigramCollocationFinder, words, n)
    top_unigrams = find_nbest_unigrams(words, n)
    return set(top_trigrams + top_bigrams_in_trigrams + top_bigrams + top_unigrams)


def profile_algo(algo, terms, sents, runs=5):
    termset = algo().add_terms(terms).build()

    times = []
    for _ in range(runs):
        start = time.time()
        for sent in sents:
            termset.query(sent)
        end = time.time()
        duration = end - start

        times.append(duration)

    ttl_time = sum(times)
    avg_time = ttl_time / runs
    memory = asizeof(termset) // 1000
    return [algo.name, f"{ttl_time:.4f}s", f"{avg_time:.4f}s", f"{memory:}k"]


def words_to_sents(words, num_words=5):
    sents = []
    total_words = len(words)
    idx = 0
    rounds = total_words // num_words

    while rounds:
        sent = " ".join(words[idx : idx + num_words])
        sents.append(sent)
        idx += num_words
        rounds -= 1

    return sents


def main(
    fileid,
    algos_to_include,
    words_per_sentence=30,
    top_ngrams=100000,
    runs=1,
):

    algos = [algo for algo in benchmark_algolist if algo.name in algos_to_include]
    corpus = gutenberg.raw(fileid)
    moby_dick = clean_text(corpus)
    words = moby_dick.split()
    sents = words_to_sents(words, num_words=words_per_sentence)
    top_ngrams = find_top_ngrams(words, top_ngrams)

    print(
        "\n".join(
            [
                f"Ngrams: {len(top_ngrams)}",
                f"Sentences: {len(sents)}",
                f"Words/sentence: {words_per_sentence}",
                f"Runs: {runs}",
            ]
        )
    )

    headers = ["name", "total time", "average time", "memory"]
    results = [profile_algo(algo, top_ngrams, sents, runs) for algo in algos]
    table = columnar(results, headers, no_borders=True, justify="r")
    print(table)
