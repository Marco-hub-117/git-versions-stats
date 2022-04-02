from tree_sitter import Language, Parser
import collections

def tokenize(path_source):
    text = bytes(read_source(path_source), 'utf8')
    tree = extract_tree(path_source)

    tokens = collections.deque()
    for node in iter_over_tree(tree):

        if node.type == 'string_literal':
            buf = text[node.start_byte:node.end_byte]
            tokens.append(buf.decode('utf-8'))

        elif not node.children and node.type == '"':
            continue
        elif not node.children and node.type == 'identifier':
            tokens.append('identifier')

        elif not node.children and node.type in ['comment', "\n"]:
            continue
        elif not node.children:
            buf = text[node.start_byte:node.end_byte]
            tokens.append(buf.decode('utf-8'))

    tokens.reverse()
    return tokens


def read_source(source_path):
    with open(source_path, 'r') as source_file:
        data = source_file.read()
    return data


def extract_tree(path_src):
    parser = build_parser()
    return parser.parse(bytes(
        read_source(path_src), 'utf8'
    ))


def build_parser():
    Language.build_library(
        # Store the library in the `build` directory
        '../build/my-languages.so',

        [
            './tree-sitter-c'
        ]
    )

    c_language = Language('../build/my-languages.so', 'c')

    language_parser = Parser()
    language_parser.set_language(c_language)

    return language_parser


def iter_over_tree(tree):
    """Iterate over this node and its children in a pre-order traversal."""
    queue = collections.deque()
    queue.append(tree.root_node)
    while len(queue) > 0:
        n = queue.pop()
        for c in n.children:
            queue.append(c)
        yield n
