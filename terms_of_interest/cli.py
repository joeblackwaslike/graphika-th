import click

from .pipeline import PipelineBuilder
from .tools.verify import ResultsVerifier
from .tools.visualize import GraphVisualizer
from .tools import benchmarks


class CLIPipeline(PipelineBuilder):
    def __init__(self, cliargs, *args, **kwargs):
        units = (
            dict(userset=cliargs["unit1_userset"], termset=cliargs["unit1_termset"]),
            dict(userset=cliargs["unit2_userset"], termset=cliargs["unit2_termset"]),
        )
        if "db_uri" in cliargs:
            kwargs["db_uri"] = cliargs["db_uri"]
        super().__init__(*args, units=units, **kwargs)

    def set_context(self, cliargs):
        return super().set_context(
            termset_algo=cliargs["termset_algo"],
            execution_date=cliargs["execution_date"],
            format_template=cliargs["format_template"],
        )


@click.group()
def cli():
    pass


@click.command("plot")
@click.argument("filepath", type=click.Path(), default="pipeline.png")
def plot(filepath):
    """Plots a graph visualization of pipeline DAG.

    FILEPATH is the name of the file to output.
    """
    PipelineBuilder().build().plot(filepath=filepath)


@click.command("verify")
@click.argument(
    "data", type=click.Path(exists=True, readable=True), required=True,
)
@click.argument(
    "results", type=click.Path(exists=True, readable=True), required=True,
)
def verify(data, results):
    """Verifies the results of `run` command.

    DATA is the path to the DATA FILE.
    RESULTS is the path to the RESULTS FILE.
    """
    with open(data) as tweets_file, open(results) as results_file:
        ResultsVerifier().run(tweets_file, results_file)


@click.command("graphvis")
@click.argument(
    "term_files",
    type=click.Path(exists=True, readable=True),
    nargs=2,
    default=["data/terms1.txt", "data/terms2.txt"],
)
def graphvis(term_files):
    """Outputs a PDF visualization of the Aho-Corasick Datastructures

    TERM_FILES is a list of paths to the termset files.
    """

    GraphVisualizer(
        filenames=["data/terms1.txt", "data/terms2.txt"]
    ).build_graphs().build_diagrams(format="pdf", auto_open=True)


@click.command("benchmark")
@click.option(
    "--top-ngrams",
    type=int,
    default=100,
    required=True,
    help="Number of ngrams to use as seed in term generation.",
)
@click.option(
    "--runs", type=int, default=1, required=True, help="Number of times to run algos."
)
@click.option(
    "--algos",
    type=str,
    default="Naive List,Naive Set,Trie,Aho-Corasick",
    required=True,
    help="Algos to include.",
)
@click.option(
    "--fileid",
    type=str,
    default="melville-moby_dick.txt",
    required=True,
    help="Gutenberg file to benchmark against.",
)
def benchmark(top_ngrams, runs, algos, fileid):
    """Benchmark and print summaries of the performance results of different data structures."""
    benchmarks.main(
        fileid=fileid,
        algos_to_include=algos.split(","),
        top_ngrams=top_ngrams,
        words_per_sentence=30,
        runs=runs,
    )


@click.command("run")
@click.argument(
    "data", type=click.Path(exists=True, readable=True), nargs=-1, required=True
)
@click.option(
    "--execution-date",
    type=click.DateTime(),
    default=None,
    help="Only process tweets for date given",
)
@click.option(
    "--format-template",
    type=str,
    default="{r.term}, {r.message_id}",
    help="String template for output",
)
@click.option(
    "--termset-algo",
    type=click.Choice(["NaiveList", "NaiveSet", "Trie", "AhoCorasick"]),
    default="AhoCorasick",
    help="Algorithm for search termsets",
)
@click.option(
    "--db-uri",
    type=str,
    default="sqlite:///:memory:",
    help="Database URI string for SQLAlchemy",
)
@click.option(
    "--unit1_userset",
    type=click.Path(exists=True, readable=True),
    default="data/nodes1.txt",
    help="File containing the node ids for unit 1",
)
@click.option(
    "--unit1_termset",
    type=click.Path(exists=True, readable=True),
    default="data/terms1.txt",
    help="File containing the terms for unit 1",
)
@click.option(
    "--unit2_userset",
    type=click.Path(exists=True, readable=True),
    default="data/nodes2.txt",
    help="File containing the node ids for unit 2",
)
@click.option(
    "--unit2_termset",
    type=click.Path(exists=True, readable=True),
    default="data/terms2.txt",
    help="File containing the terms ids for unit 2",
)
def run(data, **cliargs):
    """Runs the data processing pipeline.

    DATA is the path to the data files to be processed.
    """
    CLIPipeline(cliargs).build().set_context(cliargs).run(data)


for cmd in [plot, verify, graphvis, benchmark, run]:
    cli.add_command(cmd)
