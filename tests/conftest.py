import pytest

from terms_of_interest.matchers import SetMatcher, termset_algos


@pytest.fixture
def term_matchers():
    def _matcher_factory(terms):
        return [algo().add_terms(terms).build() for algo in termset_algos.values()]

    return _matcher_factory


@pytest.fixture
def node_matcher():
    def _node_matcher_factory(nodes):
        return SetMatcher().add_terms(nodes).build()

    return _node_matcher_factory
