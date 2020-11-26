from datetime import date, datetime

from glide import Glider, Return

from terms_of_interest.pipeline import SchemaLoad, DateFilter, UserFilter, TermFilter
from terms_of_interest.schemas import Tweet
from terms_of_interest.matchers import ACMatcher


tweet_raw = """{"text": "Florida lawmakers have introduced a law that requires physicians to obtain a parent or guardian's notarized written consent before a minor child can have an abortion. Doctors who violate the law could be charged with a felony. https://t.co/FsIletsEHV", "node_id": "14511951", "message_id": "1115339928542564352", "message_time": "Mon Apr 08 19:45:35 +0000 2019"}"""
tweet_obj = Tweet.parse_raw(tweet_raw)


def build_termset_node(terms):
    termset = ACMatcher().add_terms(terms).build()
    return TermFilter("term_filter", termset=termset)


def build_test_pipeline(node, data):
    glider = Glider(node | Return("return"))
    return glider.consume([data])


def test_SchemaLoad():
    node = SchemaLoad("schema", schema=Tweet)
    result = build_test_pipeline(node, tweet_raw)

    assert len(result) == 1
    assert isinstance(result[0].message_time, datetime)


def test_DateFilter_default():
    node = DateFilter("date_filter")
    result = build_test_pipeline(node, tweet_raw)

    assert len(result) == 1


def test_DateFilter_with_same_execution_date():
    node = DateFilter("date_filter", execution_date=date(2019, 4, 8))
    result = build_test_pipeline(node, tweet_obj)

    assert len(result) == 1


def test_DateFilter_with_other_execution_date():
    node = DateFilter("date_filter", execution_date=date(2019, 4, 9))
    result = build_test_pipeline(node, tweet_obj)

    assert len(result) == 0


def test_UserFilter_in_userset():
    node = UserFilter("user_filter", userset={"14511951"})
    result = build_test_pipeline(node, tweet_obj)

    assert len(result) == 1


def test_UserFilter_not_in_userset():
    node = UserFilter("user_filter", userset={"1234"})
    result = build_test_pipeline(node, tweet_obj)

    assert len(result) == 0


def test_TermFilter_in_termset():
    terms = {"florida lawmakers", "lawmakers", "law"}
    node = build_termset_node(terms)
    results = build_test_pipeline(node, tweet_obj)

    assert len(results) == len(terms)
    assert {r.term for r in results} == terms
    for result in results:
        assert result.message_id == tweet_obj.message_id


def test_TermFilter_not_in_termset():
    terms = {"terms not in", "the termset"}
    node = build_termset_node(terms)
    results = build_test_pipeline(node, tweet_obj)

    assert len(results) == 0
