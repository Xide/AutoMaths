"""Process the raw aggredated dataset to remove unused values."""

import re
import pandas as pd
from functools import reduce


def reindex_for_file(df):
    """Reindex tokens ids on a file."""
    sorted_df = df.sort_values('token_id')
    sorted_df['token_id'] = list(range(len(df)))
    return sorted_df


def reindex_dataset(df):
    """Delete gaps in token_id fields."""
    return reduce(
        lambda x, y: pd.concat([x, y]),
        map(
            lambda x: reindex_for_file(df[df['file_id'] == x]),
            range(len(df['file_id'].unique()))
        )
    )


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


def main(args):
    """Command line wrapper to clean a dataset."""
    print('Cleaning: loading Dataset')
    df = pd.DataFrame.from_csv(args.input)
    print('Cleaning: cleaning Dataset')
    df, _ = clean_dataset(df)
    print('Cleaning: reindexing Dataset')
    df = reindex_dataset(df)
    print('Cleaning: exporting Dataset')
    df.to_csv(args.output)
    print('Cleaning: Done')


if __name__ == '__main__':
    import sys
    import argparse

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
            '-i',
            '--input',
            type=str,
            help='path to the aggregated dataset.'
        )
        return parser
    main(generate_parser().parse_args())
    sys.exit(0)
