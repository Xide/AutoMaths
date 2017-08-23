"""Utilities to work with proofs in the dataset."""

import pandas as pd


def proofs(df):
    """Iterate over the proofs of the dataset.

    :param df: the complete dataset
    :iterator: (proof_id, definition, demonstration)
    :itype: (str, pd.DataFrame, pd.DataFrame)
    """
    proofs_df = df.dropna()
    proofs_ids = proofs_df['proof_id'].unique()

    for proof_id in proofs_ids:
        ctx = proofs_df[proofs_df['proof_id'] == proof_id]
        proof = df[df['proof_id'] == proof_id]

        start_token, proof_token, end_token = \
            (ctx[ctx['proof_context'] == x].iloc[0] for x in (
                'goal',
                'enter',
                'leave'
            ))

        ids = [int(x['token_id']) for x in (
            start_token,
            proof_token,
            end_token
        )]

        definition = proof[
            [x >= ids[0] and x < ids[1] for x in proof['token_id']]
        ]
        demonstration = proof[
            [x >= ids[1] and x < ids[2] for x in proof['token_id']]
        ]
        yield proof_id, definition, demonstration


if __name__ == '__main__':
    df = pd.DataFrame.from_csv('../../data/clean.csv')

    for x in proofs(df):
        print(x[0])
