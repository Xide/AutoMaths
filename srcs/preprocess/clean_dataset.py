"""Process the raw aggredated dataset to remove unused values."""

import re


def clean_dataset(df):
    """Remove junk from aggregated dataset."""
    clean_stats = {
        'LEXING_ERROR': 0,
        'EMPTY_TEXT': 0,
        'COMMENTS': 0
    }
    # Dropping errors from the dataset
    # TODO: Fix them instead, some file are lost in the process
    n = len(df)
    df = df[df['token'] != 'Error']
    clean_stats['LEXING_ERROR'] = n - len(df)

    # Dropping comments, unneeded in the learning process
    n = len(df)
    df = df[df['token'] != 'Comment']
    clean_stats['COMMENTS'] = n - len(df)

    # Dropping empty strings of text tokens as they are
    # irrelevent for the learning process since the input
    # is already splitted by the lexer.
    n = len(df)
    empty_string_regex = re.compile('^\s*$')
    not_empty_idxs = list(
        map(
            lambda x: empty_string_regex.match(x) is None,
            df['raw']
        )
    )
    df = df[not_empty_idxs]
    clean_stats['EMPTY_TEXT'] = n - len(df)

    return df, clean_stats
