def test_node_matcher(node_matcher):
    matcher = node_matcher(["0123456"])
    assert "0123456" in matcher


def test_node_matcher_not_in_set(node_matcher):
    matcher = node_matcher([])
    assert "0123456" not in matcher


def test_term_matchers(term_matchers):
    for matcher in term_matchers(["reminder", "espn+"]):
        results = matcher.query(
            "@haarrrisson You\u2019re all set! We\u2019ll send you a reminder on 4/13 to stream #UFC236 LIVE on ESPN+ #ItsBoutTime"
        )
        assert results == {"reminder", "espn+"}


def test_term_matchers_noterms(term_matchers):
    for matcher in term_matchers([]):
        for text in ("", " ", "hello"):
            results = matcher.query(text)
            assert isinstance(results, set)
            assert not results


def test_term_matchers_worstcase(term_matchers):
    for matcher in term_matchers(["a", "aa", "aaa", "aaaa", "a aaa aaaa"]):
        results = matcher.query("a aaa aaaa")
        assert results == {"a", "aaa", "aaaa", "a aaa aaaa"}


def test_term_matchers_overlap(term_matchers):
    for matcher in term_matchers(
        [
            "cell phones",
            "problematic cell phone",
            "tickets",
            "white sox",
            "red sox",
            "sox home opener",
            "home opener tickets",
        ]
    ):
        results = matcher.query(
            "sox fan using a problematic cell phone to order home opener tickets for the red sox opener"
        )
        assert results == {
            "problematic cell phone",
            "tickets",
            "red sox",
            "home opener tickets",
        }
