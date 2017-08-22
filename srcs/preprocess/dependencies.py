"""Coq files dependencies analysis.

..todo: Generalize multiprocessing to the whole pipeline.
"""

import copy
import itertools

import pandas as pd
import networkx as nx
import networkx.algorithms as al

from os import path
from functools import reduce, partial
from concurrent.futures import ProcessPoolExecutor


def mask(df, f, *args, **kwargs):
    """Mask a dataset.

    :param df: The pandas DataFrame to mask
    :param f: the mask function
              (will be given the DataFrame and extra args)
    :return: the masked DataFrame
    :rtype: pandas.DataFrame
    """
    return df[f(df, *args, **kwargs)]


def create_file_path(df):
    """Create path for the file imports.

    :param df: Dataframe containing all the tokens of the file
    :return: ';' separated paths required for the file imports
    :rtype: str
    """
    name_tokens = \
        df[['token_id', 'token', 'raw']][df['token'] == 'Name']
    loadpath_tokens = name_tokens[name_tokens['raw'] == 'LoadPath']

    def path_aggregator(
            row,
            df,
            context={
                'initializing': True,
                'r': ''
            }):
        """Aggregate tokens after the LoadPath.

        :param row: The row of the initial Loadpath token
        :param df: The dataframe of all the file tokens
        :return: path for the loadpath token
        :rtype: str
        """
        ctx = copy.deepcopy(context)
        next_row = df[
            df['token_id'] == (row['token_id'] + 1)
        ].iloc[0]

        if ctx['initializing'] and row['raw'] == 'LoadPath':
            # The current token is the initial LoadPath.
            ctx['initializing'] = False
            return path_aggregator(next_row, df, ctx)

        if row['token'] != 'Literal.String.Double':
            # The path is defined
            return ctx['r']

        # Concatenate result with this litteral raw.
        ctx['r'] += row['raw']
        return path_aggregator(
            next_row,
            df,
            context=ctx
        )

    # Launching the path_aggregator
    # function for each loadpath token
    paths = list(map(
        lambda r: path_aggregator(r, df),
        map(lambda x: x[1], loadpath_tokens.iterrows())
    ))

    # Building the result string by concatenating with ';'
    x = reduce(
        lambda x, y: ';'.join([x, y.replace('"', '')]),
        paths,
        '.'
    )
    return x


def dep_aggregator(
        df,
        row,
        context={'initializing': True, 'last': None, 'deps': []}
        ):
    """Aggregate dependencies after the 'Require' token.

    :param df: The tokens dataframe
    :param row: require token to process
    :rtype: list
    :return: Labels of the dependencies
    ..warning:  the raw == Structure part is a ugly hack to
                bypass lexer limitations in file
                /data/raw/HoTT/theories/Categories/Structure.v
                where Structure is recognized by pygments as a Keyword
    """
    ctx = copy.deepcopy(context)
    try:
        next_row = df[df['token_id'] == (row['token_id'] + 1)].iloc[0]
    except IndexError:
        # File has finished with an export
        return ctx['deps']

    # Debug informations
    # print(row['file_id'], row['token_id'], row['token'], row['raw'], ctx)
    if not ctx['initializing']:
        # Starting to aggregate names
        if row['token'] not in ('Name', 'Operator') and \
                row['raw'] != 'Structure':
            # End of recursion condition, return the result from context
            return ctx['deps']
        if row['token'] == 'Name' or row['raw'] == 'Structure':
            if \
                    ctx['last'] is None or \
                    ctx['last'] in ('Name', 'Keyword.Namespace'):
                # Start a new dependency
                ctx['deps'] += [row['raw']]
            else:
                # Come after a '.' operator, subpackage handling
                ctx['deps'] = ctx['deps'][:-1] + \
                    [
                        '%s.%s' % (
                            ctx['deps'][-1],
                            row['raw']
                        )
                    ]
        # Keep previous token record for parsing
        ctx['last'] = row['token']
    else:
        # Skipping namespace tokens
        if next_row['token'] != 'Keyword.Namespace' or \
                next_row['raw'] == 'Structure':
            ctx['initializing'] = False
    return dep_aggregator(df, next_row, context=ctx)


def deps_for_file(df, verbose=True):
    """Generate list of dependencies for a file.

    :param df: The DataFrame containing file tokens
    :param verbose: print the file id and path when processing
    :return: Series of dependencies labels (eg: `HoTT.HSet`)
    :rtype: `pandas.Series` of `str`
    """
    if verbose:
        print(
            '[deps] File #{} : {}'.format(
                df['file_id'].iloc[0],
                df['file'].iloc[0]
            )
        )
    namespace_tokens = \
        df[df['token'] == 'Keyword.Namespace']

    require_tokens = namespace_tokens[
        namespace_tokens['raw'] == 'Require'
    ]
    return pd.Series(reduce(
        lambda x, y: x + y,
        map(
            partial(dep_aggregator, df),
            [x[1] for x in require_tokens.iterrows()]
        ),
        []
    )).unique()


def resolve_dependencies_labels(df, root):
    """Translate require names into file indexes.

    :param df: the dataframe containing tokens + labels + paths
               labels are generated by deps_for_file
               paths are generated by create_file_path
    :param root: Path to the root directory (from the `data/raw`
                 folder) in which to resolve dependencies
    :return: list of tuples containing (file_id, list(deps_ids))
             deps_ids are the file_id on which this file depends

    :rtype: list of tuples (int, list of int)

    ..warning: This function yield some -1 dependencies indexes.
                it happens because some import cannot be resolved

    ..note: the root argument must be the same as the top level
            imports in the underlying coq files.
    """
    # Take only the part of the dataset below root
    print('Resolving dependencies below', root)

    df = mask(
        df,
        lambda x: [y.startswith(root) for y in x['file']]
    )
    reloc_df = df.copy()

    def resolve_label(row, df):
        """Resolve dependency index for one require token."""
        paths = row[1]['deps_path']
        local_dir = path.dirname(row[1]['file'])

        def resolve_one_entry(df, paths, lbl):
            """Resolve for each of the names in the require token."""
            lbl = lbl.replace('.', '/')
            for x in paths:
                if not path.isabs(x):
                    guess = path.normpath(path.join(local_dir, x))
                else:
                    guess = x
                guess = path.join(guess, lbl)
                match = df[df['file'] == guess]
                if len(match):
                    return (lbl, match)
            return (lbl, [])

        resolver = partial(
            resolve_one_entry,
            df,
            [local_dir, root] +
            [path.normpath(path.join(local_dir, x)) for x in paths]
        )

        def index_from_match(match):
            """Get file index, return [-1] for an unrecognized import."""
            match = match[1]
            if len(match) != 1:
                return [-1]
            return [match.iloc[0]['file_id']]

        return (row[1]['file_id'], reduce(
            lambda x, y: x + y,
            map(
                index_from_match,
                map(
                    resolver,
                    row[1]['deps_labels']
                )
            ),
            []
        ))

    return (list(map(
        lambda x: resolve_label(x, reloc_df),
        reloc_df.iterrows()
    )))


def dependency_graph(df, clean_graph_loops=True):
    """Generate the dependency graph of the coq files.

    :param df: the DataFrame of all the files tokens.
    :param clean_graph_loops: remove cyclic dependencies in graph
    :return: DiGraph with files id as nodes and dependencies as
             edges.
    :rtype: networkx.DiGraph
    """
    def linker(from_node, to_nodes):
        """Return a list of networkx formatted edges.

        Those edges represents the dependencies in the coq files.
        :param from_node: id of the dependent node
        :param to_nodes: list of ids of required files
        :return: list of networkx formatted edges.
        :rtype: list of tuple (int, int)

        ..note: linker is also in charge of removing the
                unknown dependencies represented by `-1` in
                the `to_nodes` list.
        """
        return map(
            lambda x: (from_node, x),
            filter(
                lambda x: x != -1,
                to_nodes
            )
        )

    def indexer(d):
        return [x[1] for x in sorted(d, key=lambda x: x[0])]

    file_ids = df['file_id'].unique()

    G = nx.DiGraph()
    G.add_nodes_from(file_ids)

    print('Generating dependencies labels for nodes')
    with ProcessPoolExecutor(max_workers=16) as executor:
        # list of slices of pandas dataframe, each containing the
        # tokens of an unique file
        file_datasets = list(map(
            lambda x: (x, df[df['file_id'] == x]),
            sorted(file_ids)
        ))

        # list of labels of the files dependencies
        labels_futures = list(map(
            lambda x: (x[0], executor.submit(deps_for_file, x[1])),
            file_datasets
        ))

        # list of relative folder to include in the file PATH
        # for imports
        loadpath_futures = list(map(
            lambda x: (x[0], executor.submit(create_file_path, x[1])),
            file_datasets
        ))

        def extract_res(x):
            r = x[1].result()
            return x[0], r

        labels = list(map(extract_res, labels_futures))
        loadpaths = list(map(extract_res, loadpath_futures))

    # Sorting the results
    labels = indexer(labels)
    loadpaths = indexer(loadpaths)

    # Creating dependency dataset (one row / file)
    deps = df[['file_id', 'file']].drop_duplicates(
        subset='file_id',
        keep='first'
    ).sort_values('file_id')

    deps['deps_labels'] = labels
    deps['deps_path'] = loadpaths

    dependencies_list = list(itertools.chain.from_iterable(
        (resolve_dependencies_labels(deps, x) for x in (
            '/HoTT/theories',
            '/UniMath/UniMath'
        ))
    ))

    edges = itertools.chain.from_iterable(map(
        lambda x: linker(*x),
        dependencies_list
    ))
    G.add_edges_from(edges)

    if clean_graph_loops:
        for c in al.simple_cycles(G):
            print('Cycle detected:', c)
            cycle_edges = [
                (c[x], c[(x + 1) % len(c)]) for x in range(len(c))
            ]
            print('Removing edges:', cycle_edges)
            G.remove_edges_from(cycle_edges)

    return G


def rec_deps(graph, n, context={}):
    """Aggregate the dependencies in a (count, deps) list."""
    def merge_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z
    ctx = context.copy()
    succs = graph.neighbors(n)
    if n not in ctx:
        # The value wasn't yet computed
        if any([x not in ctx for x in succs]):
            # One dependency has not been resolved
            ctx = reduce(
                lambda x, y:
                    merge_dicts(
                        x,
                        rec_deps(
                            graph,
                            y,
                            context=ctx
                        )
                    ),
                succs,
                ctx
            )
        # Putting number of dependencies and
        # direct dependencies indexes in a tuple at key `n`
        ctx[n] = (
            len(succs) + sum(
                [ctx[y][0] for y in succs]
            ),
            succs
        )
    return ctx


if __name__ == '__main__':
    import argparse

    def generate_parser():
        """Generate an argument parser for dependency cli."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'source',
            type=str,
            help='Path to the cleaned dataset'
        )
        parser.add_argument(
            '-o',
            '--output',
            type=str,
            help='file in which to export the graph (gexf format)'
        )
        return parser

    args = generate_parser().parse_args()
    print('Loading dataframe into memory')
    df = pd.DataFrame.from_csv(args.source)
    print('Generating dependency graph from dataset.')

    graph = dependency_graph(df)
    deps = reduce(
        lambda x, y: rec_deps(graph, y, context=x),
        graph.nodes(),
        {}
    )
    deps = sorted(deps.items(), key=lambda x: x[1])
    print(deps)
