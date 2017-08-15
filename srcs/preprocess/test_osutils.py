"""Testing suite for data pre-processing."""

import os
import shutil
import unittest

from functools import partial

from osutils import \
    find_files

# Adapting this test with the coq file pattern fixed into find_files
coq_files = partial(find_files, regex='^.*\.v$')


def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    """
    Equivalent of UNIX touch command.

    Taken from :
    https://stackoverflow.com/questions/1158076/implement-touch-using-python
    """
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(
            f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd,
            **kwargs
        )


class TestCoqFilesIteration(unittest.TestCase):
    """Test the `coq_files` function from preprocessing."""

    def setUp(self):
        """Create the test directory layout."""
        self.basepath = '/tmp/coq_files_iterator_tests'

        # Create root directory
        try:
            os.mkdir(self.basepath)
        except FileExistsError:
            shutil.rmtree(self.basepath)
            os.mkdir(self.basepath)

        # Create tests directories
        paths = list(map(
            lambda x: os.path.join(self.basepath, x),
            [
                'test_single',
                'test_multiple',
                'test_ignore_fileext',
                'test_recursive',
                'test_relative_path'
            ]
        ))

        # Create directories
        list(map(
            lambda x: os.mkdir(x),
            paths
        ))

        # Create a valid coq file in each directory
        list(map(
            lambda x: touch(os.path.join(x, 'valid.v')),
            paths
        ))

        # test_multiple
        touch(os.path.join(self.basepath, 'test_multiple', 'valid2.v'))
        touch(os.path.join(self.basepath, 'test_multiple', 'valid3.v'))

        # test_ignore_fileext
        touch(os.path.join(self.basepath, 'test_ignore_fileext', 'invalid.x'))

        # test_recursive
        os.mkdir(os.path.join(self.basepath, 'test_recursive', 'subfolder'))
        touch(os.path.join(
            self.basepath,
            'test_recursive',
            'subfolder',
            'valid.v'
            ))

        # test_relative_path
        os.mkdir(
            os.path.join(
                self.basepath,
                'test_relative_path',
                'subfolder'
            )
        )
        touch(
            os.path.join(
                self.basepath,
                'test_relative_path',
                'subfolder',
                'valid.v'
            )
        )

    def tearDown(self):
        """Remove the test directory layout."""
        # shutil.rmtree(self.basepath)

    def test_single(self):
        """Test for a single coq file in a folder."""
        self.assertEqual(
            len(list(
                coq_files(
                    os.path.join(self.basepath, 'test_single'),
                    recursive=False
                )
            )),
            1,
            msg='Should find one valid file in test_single folder.'
        )

    def test_multiple(self):
        """Test for multiple coq files in a folder."""
        self.assertEqual(
            len(list(
                coq_files(
                    os.path.join(self.basepath, 'test_multiple'),
                    recursive=False
                )
            )),
            3,
            msg='Should find three valid files in test_multiple folder.'
        )

    def test_ignore_fileext(self):
        """Test that non-Coq files are ignored."""
        self.assertEqual(
            len(list(
                coq_files(
                    os.path.join(self.basepath, 'test_ignore_fileext'),
                    recursive=False
                )
            )),
            1,
            msg='Should not count invalid.x in valid coq files.'
        )

    def test_recursive(self):
        """Test that recursive mode is working."""
        self.assertEqual(
            len(list(
                coq_files(
                    os.path.join(self.basepath, 'test_recursive'),
                    recursive=True
                )
            )),
            2,
            msg='Should see the valid file in subfolder.'
        )

    def test_relative_path(self):
        """Test that path is relative to current directory."""
        working_dir = os.getcwd()
        os.chdir(os.path.join(self.basepath, 'test_relative_path'))
        self.assertEqual(
            len(list(
                coq_files(
                    os.path.join('subfolder'),
                    recursive=True
                )
            )),
            1,
            msg='Should see the valid file in relative subfolder.'
        )
        os.chdir(working_dir)
