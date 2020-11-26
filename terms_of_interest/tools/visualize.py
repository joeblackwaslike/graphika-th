from queue import Queue

from graphviz import Digraph

from ..matchers import ACMatcher


class GraphVisualizer:
    graph_factory = ACMatcher

    def __init__(self, filenames=("data/terms1.txt", "data/terms2.txt")):
        self.filenames = filenames
        self.graphs = {}

    def build_graphs(self):
        for filename in self.filenames:
            name = filename.split("/")[1].split(".")[0]
            self.graphs[name] = ACMatcher.from_txtfile(filename)
        return self

    def build_diagrams(self, format="pdf", auto_open=True):
        for name, graph in self.graphs.items():
            self.build_diagram(name, graph, format, auto_open)

    def build_diagram(self, name, graph, format, auto_open):
        filename = name + ".gv"
        diagram = Digraph(filename=filename, format=format)
        diagram.attr("node", fontsize="10")
        diagram.attr("edge", arrowsize="0.3")

        q = Queue()
        q.put((graph.root, None))

        while not q.empty():
            node, parent_id = q.get()

            if node.terms:
                diagram.node(
                    str(id(node)),
                    f"value: {node.value}\nterms: {','.join(list(node.terms))}",
                    shape="doublecircle",
                )
            else:
                diagram.node(str(id(node)), node.value)

            if parent_id:
                diagram.edge(parent_id, str(id(node)), "child")

            if node.fail:
                diagram.edge(str(id(node)), str(id(node.fail)), "fail", color="blue")

            for child in node.children.values():
                q.put((child, str(id(node))))

        with open(filename, "w") as fd:
            fd.write(diagram.source)
            diagram.render(filename, view=auto_open)

    def visualize(self):
        self.build_graphs().build_diagrams()
