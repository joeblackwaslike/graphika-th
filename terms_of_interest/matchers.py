from __future__ import annotations

from typing import Iterable
import collections

from . import util
from .tokenizers import NaiveTokenizer, NgramTokenizer


class Matcher:
    def __init__(self):
        self.terms = []

    def add_term(self, term: str) -> None:
        self.terms.append(term)

    def add_terms(self, terms: Iterable[str]) -> Matcher:
        for term in terms:
            self.add_term(term)
        return self

    def build(self) -> Matcher:
        return self

    def __repr__(self):
        return f"{type(self).__name__}(terms: {', '.join(self.terms)})"

    @classmethod
    def from_txtfile(cls, filepath: str) -> Matcher:
        matcher = cls()
        for line in util.readlines(filepath):
            matcher.add_term(line)
        matcher.build()
        return matcher


class SetMatcher(Matcher):
    name = "Set"

    def __init__(self):
        self.terms = set()

    def add_term(self, term: str) -> None:
        self.terms.add(term)

    def contains(self, item):
        return item in self.terms

    def __contains__(self, item):
        return self.contains(item)


class NaiveListMatcher(Matcher):
    """Term matcher implementation using a Naive List

    n = number of terms
    m = number of ngrams in terms
    q = number of ngrams in query text (haystack)
    r = number of results returned

    Build:
      Time: O(n + m)
      Space: O(n + m)

    Query:
      Time: O(qm)
      Space: O(r)
    """

    name = "Naive List"

    def __init__(self, ngram_tokenizer=NgramTokenizer()):
        self.ngram_tokenizer = ngram_tokenizer
        super().__init__()

    def query(self, text):
        results = set()
        for ngram in self.ngram_tokenizer.tokenize(text):
            if ngram in self.terms:
                results.add(ngram)
        return results


class NaiveSetMatcher(SetMatcher):
    """Term matcher implementation using a Naive Set

    n = number of terms
    m = number of ngrams in terms
    q = number of ngrams in query text (haystack)
    r = number of results returned

    Build:
      Time: O(n + m)
      Space: O(n + m)

    Query:
      Time: O(q)
      Space: O(q + r)
    """

    name = "Naive Set"

    def __init__(self, ngram_tokenizer=NgramTokenizer()):
        self.ngram_tokenizer = ngram_tokenizer
        super().__init__()

    def query(self, text):
        return set(self.ngram_tokenizer.tokenize(text)) & self.terms


class TrieNode:
    """"Trie Node"""

    def __init__(self, value):
        self.value = value
        self.children = {}
        self.terms = set()

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"


class ACNode(TrieNode):
    """Aho-Corasick Automaton Node"""

    def __init__(self, value):
        super().__init__(value)
        self.fail = None


class TrieMatcher(Matcher):
    """Term matcher implementation using a Keyword Trie

    n = number of terms
    m = number of nodes in trie (roughly equal to total number of words in terms)
    w = number of words in query text (haystack)
    r = number of results returned

    Build:
      Time: O(n)
      Space: O(n + m)

    Query:
      Time: O(w) Best Case, worse with increased backtracking
      Space: O(w + r)
    """

    name = "Trie"
    _node_factory = TrieNode

    def __init__(self, tokenizer=NaiveTokenizer()):
        self.tokenizer = tokenizer
        self.root = self._node_factory("")

    def add_term(self, term):
        node = self.root
        for word in self.tokenizer.tokenize(term):
            if word not in node.children:
                node.children[word] = self._node_factory(word)
            node = node.children[word]
        node.terms.add(term)

    def query(self, text):
        results = set()
        words = tuple(self.tokenizer.tokenize(text))
        node = self.root

        for idx, word in enumerate(words):
            cur_node = node
            while word in cur_node.children:
                cur_node = cur_node.children[word]

                if cur_node.terms:
                    results.update(cur_node.terms)

                if idx + 1 >= len(words):
                    break
                else:
                    idx += 1
                    word = words[idx]

        return results

    def __repr__(self):
        return f"{type(self).__name__}(children: {', '.join(self.root.children)})"


class ACMatcher(TrieMatcher):
    """Term matcher implementation using Aho-Corasick Automaton

    Since matches exist only on word boundaries, each node only stores a
    complete word rather than a single character.

    n = number of terms
    m = number of nodes in automaton (roughly equal to total number of words in terms)
    w = number of words in query text (haystack)
    r = number of results returned

    Build:
      Time: O(n + m)
      Space: O(n + m)

    Query:
      Time: O(w) Best & Worst Case
      Space: O(r)
    """

    name = "Aho-Corasick"
    _node_factory = ACNode

    def build(self):
        super().build()

        self.root.fail = self.root

        queue = collections.deque()
        for node in self.root.children.values():
            node.fail = self.root
            queue.append(node)

        while queue:
            node = queue.popleft()
            for word, child in node.children.items():
                child.fail = (
                    node.fail.children.get(word)
                    or self.root.children.get(word)
                    or self.root
                )
                if child.fail.terms:
                    child.terms.update(child.fail.terms)
                queue.append(child)

        return self

    def query(self, text):
        results = set()
        node = self.root

        for word in self.tokenizer.tokenize(text):
            node = node.children.get(word) or node.fail.children.get(word) or self.root
            results.update(node.terms)

        return results


termset_algos = {
    "naivelist": NaiveListMatcher,
    "naiveset": NaiveSetMatcher,
    "ahocorasick": ACMatcher,
    "trie": TrieMatcher,
}
benchmark_algolist = [NaiveListMatcher, NaiveSetMatcher, TrieMatcher, ACMatcher]
