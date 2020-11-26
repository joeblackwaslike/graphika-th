# Graphika Take Home Assignment (Terms of Interest)
### by Joe Black
me@joeblack.nyc | 646.924.7718

## Design docs
Design documents and answers to take-home questions are located in [design/README.md](design/README.md)

## Installation
Note: Tested on python 3.8 only!
```bash
# Create new virtual environment
python -m venv venv
source venv/bin/activate

# To install minimum requirements
pip install .

# To install additional benchmarking and visualization requirements
pip install ".[all]"
```

## Usage
The CLI interface is accessible via `toi`
```
Usage: toi [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  benchmark  Benchmark and print summaries of the performance results of...
  graphvis   Outputs a PDF visualization of the Aho-Corasick Datastructures...
  plot       Plots a graph visualization of pipeline DAG.
  run        Runs the data processing pipeline.
  verify     Verifies the results of `run` command.
```

### Commands
#### Run
This command runs the pipeline.  This is the main subcommand.
```
Usage: toi run [OPTIONS] DATA...

  Runs the data processing pipeline.

  DATA is the path to the data files to be processed.

Options:
  --execution-date [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                  Only process tweets for date given
  --format-template TEXT          String template for output
  --termset-algo [NaiveList|NaiveSet|Trie|AhoCorasick]
                                  Algorithm for search termsets
  --db-uri TEXT                   Database URI string for SQLAlchemy
  --unit1_userset PATH            File containing the node ids for unit 1
  --unit1_termset PATH            File containing the terms for unit 1
  --unit2_userset PATH            File containing the node ids for unit 2
  --unit2_termset PATH            File containing the terms ids for unit 2
  --help                          Show this message and exit.
```

##### Examples
###### Just process tweets from `data/tweets.jsonl`
```bash
$ toi run data/tweets.jsonl
```
```
les miserables, 1116190735336968192
espn+, 1116191634390159362
espn+, 1116192735332065280
...
baseball, 1115342242041028610
espn+, 1115341648114987008
espn+, 1115342224114495491
```

###### Process only a days worth of data (for nightly jobs)
```bash
$ toi run --execution-date "2019-04-10" data/tweets.jsonl
```
```
problematic cell phone, 1116077167102836736
wnba, 1116077164821143553
cardinals, 1116076943340736512
...
espn+, 1116077671472144392
pga, 1116078313016053760
baseball, 1116078313779474433
```

###### Use custom nodesets and termsets
```bash
$ toi run \
    --unit1_userset data/nodes1.txt \
    --unit1_termset data/terms1.txt \
    --unit2_userset data/nodes2.txt \
    --unit2_termset data/terms2.txt data/tweets.jsonl
```
```
les miserables, 1116190735336968192
espn+, 1116191634390159362
espn+, 1116192735332065280
...
baseball, 1115342242041028610
espn+, 1115341648114987008
espn+, 1115342224114495491
```

#### Plot
This command outputs a diagram of the pipeline DAG in png format.
```
Usage: toi plot [OPTIONS] [FILEPATH]

  Plots a graph visualization of pipeline DAG.

  FILEPATH is the name of the file to output.

Options:
  --help  Show this message and exit.
```

#### Verify
This command can be used to verify the results of the pipeline.
```
Usage: toi verify [OPTIONS] DATA RESULTS

  Verifies the results of `run` command.

  DATA is the path to the DATA FILE. RESULTS is the path to the RESULTS
  FILE.

Options:
  --help  Show this message and exit.
```

##### Examples
###### Verify the results of `run` command
```bash
$ toi run data/tweets.jsonl > results.txt
$ toi verify data/tweets.jsonl results.txt
```

#### Benchmark
This command runs basic performance benchmarks for different data structure implementations.
```
Usage: toi benchmark [OPTIONS]

  Benchmark and print summaries of the performance results of different data
  structures.

Options:
  --top-ngrams INTEGER  Number of ngrams to use as seed in term generation.
                        [required]

  --runs INTEGER        Number of times to run algos.  [required]
  --algos TEXT          Algos to include.  [required]
  --fileid TEXT         Gutenberg file to benchmark against.  [required]
  --help                Show this message and exit.
```

##### Examples
Note: You may need to download the gutenberg corpus using nltk.download to run benchmarks!

###### All data structures using 100 top ngrams
```bash
$ toi benchmark \
    --algos "Naive List,Naive Set,Trie,Aho-Corasick" \
    --fileid melville-moby_dick.txt \
    --top-ngrams 100
```
```
Ngrams: 452
Sentences: 7067
Words/sentence: 30
Runs: 1

          NAME  TOTAL TIME  AVERAGE TIME  MEMORY

    Naive List     3.6984s       3.6984s     35k
     Naive Set     0.3618s       0.3618s     64k
          Trie     0.0928s       0.0928s    455k
  Aho-Corasick     0.0950s       0.0950s    455k
```

###### All data structures using 1000 top ngrams
```bash
$ toi benchmark \
    --algos "Naive List,Naive Set,Trie,Aho-Corasick" \
    --fileid melville-moby_dick.txt \
    --top-ngrams 1000
```
```
Ngrams: 4311
Sentences: 7067
Words/sentence: 30
Runs: 1

          NAME  TOTAL TIME  AVERAGE TIME  MEMORY

    Naive List    33.2899s      33.2899s    332k
     Naive Set     0.3590s       0.3590s    425k
          Trie     0.1257s       0.1257s   4181k
  Aho-Corasick     0.1013s       0.1013s   4181k
```

*NOTE: Further examples will drop 'Naive List' since it scales poorly and doesn't finish in any amount of reasonable time.*

###### Set,Trie,Aho-Corasick using 300,000 top ngrams
```bash
$ toi benchmark \
    --algos "Naive Set,Trie,Aho-Corasick" \
    --fileid melville-moby_dick.txt \
    --top-ngrams 300000
```
```
Ngrams: 327659
Sentences: 7067
Words/sentence: 30
Runs: 1

          NAME  TOTAL TIME  AVERAGE TIME   MEMORY

     Naive Set     0.5133s       0.5133s   38495k
          Trie     0.6799s       0.6799s  209709k
  Aho-Corasick     0.2964s       0.2964s  102284k
```

###### Set,Trie,Aho-Corasick using 300,000 top ngrams @ 100 runs
```bash
$ toi benchmark \
    --algos "Naive Set,Trie,Aho-Corasick" \
    --fileid melville-moby_dick.txt \
    --top-ngrams 300000 \
    --runs 10
```
```
Ngrams: 327659
Sentences: 7067
Words/sentence: 30
Runs: 10

          NAME  TOTAL TIME  AVERAGE TIME   MEMORY

     Naive Set     5.0387s       0.5039s   38495k
          Trie     6.7984s       0.6798s  209709k
  Aho-Corasick     3.2405s       0.3241s  109313k
```

#### Graphvis
This command will output a diagram of the Aho-Corasick automaton in PDF format.  It helps alot with visualizing how the data structure works.
```
Usage: toi graphvis [OPTIONS] [TERM_FILES]...

  Outputs a PDF visualization of the Aho-Corasick Datastructures

  TERM_FILES is a list of paths to the termset files.

Options:
  --help  Show this message and exit.
```

## Testing
Basic tests available at `tests/`.  Run them via pytest.
```bash
$ python -m pytest tests
```

## TODO
Things I would do with more time:
- [] Twitter firehose stream as data source.
- [] Add parallel processing to pipeline via Dask/Celery/Redis.
- [] Pickle/cache data-structures for nodesets and termsets.
- [] Add logging.
- [] More testing.
- [] Better results verifier.
- [] Better benchmarking.
- [] Load results to Postgres or InfluxDB.
- [] Add advanced taco making capabilities.
