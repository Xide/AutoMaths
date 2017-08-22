"""Aggregate raw objects into a single csv dataset."""

import json
import uuid
import argparse
import itertools
import pandas as pd
from os import path
from osutils import find_files

dataset_columns = [
    'file_id',
    'token_id',
    'file',
    'token',
    'raw',
    'proof_context',
    'proof_id'
]


def infiniteof(expr):
    """Generate it's parameter forever."""
    while True:
        yield expr


def incrementer():
    """Return a function incrementing the same variable."""
    x = 0

    def fn():
        nonlocal x
        x += 1
        return str(x)

    return fn


def generate_df_for_file(fname, file_index=None, root=None):
    """
    Create DataFrame from raw tokens in a file.

    Generate intermediate lists to label the proofs in the dataset


    :param fname: path of the raw dataset
    :param file_index: global_index of the current_file
        default: `uuid.uuid4()`
    :param root: root folder to remove in the final path.
    :rtype: pandas.DataFrame
    :return: DataFrame of this file tokens with labels
    .. note:: this create 3 intermediate lists
                - list of tokens indexes of flow control
                - list of tokens indexes where prooving start
                - list of tokens indexes where definitions start

    .. todo:: refactor intermediate lists to be evaluated lazily
    """
    if file_index is None:
        file_index = str(uuid.uuid4())

    with open(fname, 'r') as f:
        j = json.load(f)

    fmt_fname = path.splitext(
        fname[len(path.abspath(root)):] if root is not None else fname
    )[0]

    # Little hack here because Abort is not considered as
    # a flow control token, but it clashes with it's usage in
    # the HoTT library.
    flow_idxs = [
        x[0] for x in enumerate(j['contents'])
        if x[1][0] == "Keyword.Namespace" or
        x[1] == ["Name", "Abort"]
    ]

    proofs_idxs = [
        x[0] for x in enumerate(j['contents'])
        if x[1] == ["Keyword.Namespace", "Proof"]
    ]

    definitions_idx = [
        x[-1] for x in
        map(lambda idx: [x for x in flow_idxs if x < idx], proofs_idxs)
        ]

    end_idx = [
        x[0] for x in
        map(lambda idx: [x for x in flow_idxs if x > idx], proofs_idxs)
    ]

    proofs = list(zip(definitions_idx, proofs_idxs, end_idx))
    proofs_flat = list(itertools.chain.from_iterable(proofs))
    proof_ids = list(map(lambda x: uuid.uuid4(), range(len(proofs))))

    def labeler(x):
        """Label each token in a proof with the corresponding id."""
        idx, content = x

        for pidx, p in enumerate(proofs):
            if p[0] <= idx <= p[2]:
                return proof_ids[pidx]
        return None

    def context_setter(x):
        """Label the flow of a proof."""
        idx, content = x
        contexts = ['goal', 'enter', 'leave']

        if idx in proofs_flat:
            proof_context = proofs_flat.index(idx) % 3
            return contexts[proof_context]
        return None

    assert all((x[0] < x[1] < x[2] for x in proofs))
    return pd.DataFrame.from_records(
        columns=dataset_columns,

        data=zip(
            infiniteof(int(file_index)),
            map(int, range(len(j['contents']))),
            infiniteof(fmt_fname),
            [x[0] for x in j['contents']],
            [x[1] for x in j['contents']],
            map(context_setter, enumerate(j['contents'])),
            map(labeler, enumerate(j['contents']))
        )
    )


def generate_parser():
    """Generate cli parsing."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='Destination of the processed file',
        default='out.om'
    )

    parser.add_argument(
        '-s',
        '--source',
        type=str,
        help='Source directory of the coq files'
    )
    return parser


if __name__ == '__main__':
    args = generate_parser().parse_args()

    df = pd.DataFrame(columns=dataset_columns)
    for idx, fname in enumerate(find_files(
            args.source,
            regex='^.*\.vo$'
            )):
            print('[{}] {}'.format(idx, fname), end='\n')
            try:
                df = df.append(
                    generate_df_for_file(fname, idx, root=args.source)
                )
            except RuntimeError:
                print('Failed to generate dataset for', fname)
                raise
    print('Exporting dataset to CSV')
    df.to_csv(args.output)
