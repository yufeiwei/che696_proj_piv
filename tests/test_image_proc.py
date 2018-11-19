#!/usr/bin/env python3
"""
Unit and regression test for the che696_proj_yufei package.
"""

# Import package, test suite, and other packages as needed
import errno
import os
import sys
import unittest
from contextlib import contextmanager
from io import StringIO
import numpy as np
import logging
from che696_proj_yufei.image_proc import main, piv_analysis

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DISABLE_REMOVE = logger.isEnabledFor(logging.DEBUG)

CURRENT_DIR = os.path.dirname(__file__)
MAIN_DIR = os.path.join(CURRENT_DIR, '..')
TEST_DATA_DIR = os.path.join(CURRENT_DIR, 'data_proc')
PROJ_DIR = os.path.join(MAIN_DIR, 'che696_proj_yufei')
DATA_DIR = os.path.join(PROJ_DIR, 'data')
SAMPLE_DATA_FILE_LOC = [os.path.join(DATA_DIR, 'sample_im1.bmp'), os.path.join(DATA_DIR, 'sample_im2.bmp')]

# Assumes running tests from the main directory
DEF_CSV_OUT = os.path.join(MAIN_DIR, 'test_piv_results.csv')
DEF_PNG_OUT = os.path.join(MAIN_DIR, 'test_piv_plot.png')

def silent_remove(filename, disable=False):
    """
    Removes the target file name, catching and ignoring errors that indicate that the
    file does not exist.

    @param filename: The file to remove.
    @param disable: boolean to flag if want to disable removal
    """
    if not disable:
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

class TestMain(unittest.TestCase):
    # These tests make sure that the program can run properly from main
    def testSampleData(self):
        # Checks that runs with defaults and that files are created
        test_input = ["-m", SAMPLE_DATA_FILE_LOC[0], SAMPLE_DATA_FILE_LOC[1]]
        try:
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
            # checks that the expected message is sent to standard out
            with capture_stdout(main, test_input) as output:
                self.assertTrue("test_piv_results.csv" in output)

            self.assertTrue(os.path.isfile("test_piv_results.csv"))
            self.assertTrue(os.path.isfile("test_piv_plot.png"))
        finally:
            silent_remove(DEF_CSV_OUT, disable=DISABLE_REMOVE)
            silent_remove(DEF_PNG_OUT, disable=DISABLE_REMOVE)

class TestMainFailWell(unittest.TestCase):
    def testMissingFile(self):
        test_input = ["-m", "ghost.bmp"]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("ghost.bmp" in output)

    def testDataDiffNumCols(self):
        input_file = os.path.join(TEST_DATA_DIR, "sample_data3_diff_cols.csv")
        test_input = ["-c", input_file]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("Wrong number of columns" in output)

















class TestQuote(unittest.TestCase):
    def testNoArgs(self):
        test_input = []
        main(test_input)
        with capture_stdout(main, test_input) as output:
            self.assertTrue("Henry David Thoreau" in output)


    def testNoAttribution(self):
        test_input = ["-n"]
        main(test_input)
        with capture_stdout(main, test_input) as output:
            self.assertFalse("Henry David Thoreau" in output)


# Utility functions

# From http://schinckel.net/2013/04/15/capture-and-test-sys.stdout-sys.stderr-in-unittest.testcase/
@contextmanager
def capture_stdout(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out
