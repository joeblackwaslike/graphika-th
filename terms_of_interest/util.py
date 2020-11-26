import ujson


def process_file(path, line_filter, line_map=None):
    with open(path) as fd:
        for line in fd:
            line = line.rstrip()
            if line_filter(line):
                yield line_map(line) if line_map else line


def readlines(path):
    yield from process_file(path, bool)


def readtweets(path):
    yield from process_file(path, bool, ujson.loads)
