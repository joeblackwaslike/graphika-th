from collections import namedtuple
import functools

from glide import Glider, Node, FileExtract, FormatPrint

from . import db
from .schemas import Tweet
from .matchers import SetMatcher, ACMatcher, termset_algos


class SchemaLoad(Node):
    def run(self, data, schema: Tweet):
        tweet = schema.parse_raw(data)
        self.push(tweet)


class DateFilter(Node):
    def run(self, data, execution_date=None):
        if not execution_date or (
            execution_date and data.message_time.date() == execution_date
        ):
            self.push(data)


class UserFilter(Node):
    def run(self, data, userset: SetMatcher):
        if data.node_id in userset:
            self.push(data)


class TermFilter(Node):
    MatchResult = namedtuple("MatchResult", ["term", "message_id"])

    def run(self, data, termset: ACMatcher):
        for match in termset.query(data.text):
            result = self.MatchResult(match.lower(), data.message_id)
            self.push(result)


class SALoader(Node):
    def run(self, data, db_session, db_model):
        obj = db_model(**data._asdict())
        db_session.add(obj)
        results = db_session.commit()
        self.push(results)


class PipelineBuilder:
    default_units = (
        dict(userset="data/nodes1.txt", termset="data/terms1.txt"),
        dict(userset="data/nodes2.txt", termset="data/terms2.txt"),
    )

    def __init__(
        self,
        schema=Tweet,
        db_uri="sqlite:///:memory:",
        db_model=db.Results,
        units=default_units,
    ):
        self.schema = schema
        self.db = db.DataAccessLayer(db_uri).connect()
        self.db_model = db_model
        self.units = units

    @staticmethod
    def format_result(r, template):
        return template.format(r=r)

    def build_units(self):
        def build_unit(idx):
            return UserFilter(f"nodes{idx}") | TermFilter(f"terms{idx}")

        return [build_unit(idx) for idx, _ in enumerate(self.units, start=1)]

    # SALoader("sql_load", db_model=self.db_model)
    def build(self):
        self.pipeline = Glider(
            FileExtract("extract", push_lines=True)
            | SchemaLoad("schema", schema=self.schema)
            | DateFilter("date_filter")
            | self.build_units()
            | [FormatPrint("print")],
            global_state={"db_session": self.db.Session()},
        )
        return self

    def set_context(
        self,
        termset_algo="AhoCorasick",
        format_template="{r.term}, {r.message_id}",
        execution_date=None,
    ):
        TermsetMatcher = termset_algos[termset_algo.lower()]
        if execution_date:
            execution_date = execution_date.date()

        self.context = {
            "date_filter": {"execution_date": execution_date},
            "print": {
                "format_func": functools.partial(
                    self.format_result, template=format_template
                )
            },
        }
        for idx, unit in enumerate(self.units, start=1):
            nodes_key = f"nodes{idx}"
            self.context[nodes_key] = dict(
                userset=SetMatcher.from_txtfile(unit["userset"])
            )
            terms_key = f"terms{idx}"
            self.context[terms_key] = dict(
                termset=TermsetMatcher.from_txtfile(unit["termset"])
            )

        return self

    def run(self, data):
        self.pipeline.consume(data, **self.context)

    def plot(self, filepath="pipeline.png"):
        self.pipeline.plot(filepath)
