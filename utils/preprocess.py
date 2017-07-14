"""
Data pre-processing module.

This module is intented to preprocess raw COQ .v files into CSV ones.
"""

import os
import re
import sys
import argparse
import logging

from pygments import highlight
from pygments.lexers.theorem import CoqLexer
from pygments.formatters import RawTokenFormatter

from osutils import find_files

log = None


def generate_parser():
    """Return the argv parser for pre-processing."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'data_directory',
        help='Directory where data was downloaded'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        help='How verbose the application should be. -vvv for max'
    )
    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='Search for files in subdirectories of `data_directory`'
    )
    return parser


def setup_logger(verbose: int):
    """
    Configure the python logger.

    :params verbose: `int` between 0 and 3.
    """
    if verbose > 3:
        verbose = 3
    verbose_levels = [
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG
    ]
    global log
    log = logging.getLogger('preprocess')
    log.setLevel(verbose_levels[verbose])
    try:
        import coloredlogs
        coloredlogs.install(
            level=verbose_levels[verbose],
            logger=log
        )
    except ImportError:
        pass


class ProofLogger:
    """Filter parts of COQ tokens that are proofs."""

    def __init__(self, log_fn=None):
        """
        Initialize the filer.

        :params fuction used to log
        :type function(str)
        """
        self.is_in_proof = False
        self.log_fn = log_fn

    def feed(self, token, raw):
        """Feed logger with raw datas."""
        # Debug: Print every proof found in the token stream
        if not self.log_fn:
            return
        if token == 'Keyword.Namespace' and 'Proof' in raw:
            self.is_in_proof = True
            self.log_fn('>>>')
        if self.is_in_proof:
            self.log_fn('token: "{}", raw: "{}"'.format(token, raw))
        if token == 'Keyword.Namespace' and \
                ('Qed' in raw or 'Defined' in raw):
            self.is_in_proof = False
            self.log_fn('<<<')


if __name__ == '__main__':
    # Parse command line arguments
    args = generate_parser().parse_args()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.isabs(args.data_directory):
        data_dir = args.data_directory
    else:
        data_dir = os.path.realpath(
            os.path.join(os.getcwd(), args.data_directory)
        )

    if not args.verbose:
        args.verbose = 0
    setup_logger(args.verbose)

    for fname in \
            find_files(
                data_dir,
                regex='^.*\.v$',
                recursive=args.recursive
            ):
        log.info('[PARSING] {}'.format(fname))
        with open(fname, 'r') as f:
            file_content = f.read()

        # `Pygments` lexing.
        lexed_content = highlight(
            file_content,
            CoqLexer(),
            RawTokenFormatter()
        )

        # Regular expression matching a raw token line.
        regex = re.compile('Token\.((?:\w+\.?)+)\s(.*)\n?')

        # Debug, write the token stream generated by pygments into text file.
        # change extension of exported file from `.v` to `.om`
        with open(
                '{}.om'.format(
                    '.'.join(fname.split('.')[:-1])
                    ),
                'wb'
                ) as f:
            f.write(lexed_content)

        # Load the entire file contents into RAM as string
        # IMPROVMENT: Enhance the `RawTokenFormatter` class to stream this data
        parsed_content = str(lexed_content, encoding='utf-8')
        parsed_tab = parsed_content.splitlines()
        proof_logger = ProofLogger()
        with open(
                '{}.ans'.format(
                    '.'.join(fname.split('.')[:-1])
                    ),
                'w'
                ) as f:
            # Iterate over every token
            for line in parsed_tab:
                match = regex.match(line)

                # If the line format does not fit with regex, raise an error
                # and exit the application
                if match is None:
                    log.error(
                        'Line "{}" does not fit with the regex.'.format(line)
                    )
                    sys.exit(1)

                # Extract groups from the regex
                token, raw = match.group(1), match.group(2)

                # Log them if they are part of a proof
                proof_logger.feed(token, raw)

                # Write the token into file for analysis
                f.write('{}\n'.format(token))
