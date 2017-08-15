"""Operating system utilities."""

import os
import re


def find_files(folder, regex='^.*$', recursive=True):
    """
    Yield the absolute path to files within `folder` matching `regex`.

    :params folder: the base folder to search in.
    :params regex: filter the files.
        NOTE: paths given to the regex are absolute.
    :params recursive: explore subdirectories.
        :default True

    NOTE: By default, if folder is relative (e.g: "./foo"), it will
    be relative to the current directory yielded by `os.getcwd`.
    NOTE: Those files are not open, only the filename is yielded
    """
    file_regex = re.compile(regex)
    if not os.path.isabs(folder):
        folder = os.path.join(os.getcwd(), folder)

    def listdir_abs(folder):
        """Yield a list of the absolute paths within `folder`."""
        return \
            map(
                lambda x: os.path.join(folder, x),
                os.listdir(folder)
            )

    # Iterating over top level directory files
    for f in filter(
        lambda x: file_regex.match(x),
        filter(
            lambda x: os.path.isfile(x),
            listdir_abs(folder)
        )
    ):
        yield f

    if recursive:
        # Iterating over subdirectories
        for f in filter(
            lambda x: os.path.isdir(x),
            listdir_abs(folder)
        ):
            # Flatten results
            for p in \
                    find_files(
                        f,
                        regex=regex,
                        recursive=recursive
                    ):
                yield p
