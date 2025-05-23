#!/usr/bin/env python3

"""Unit tests for interpreter module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import logging
from unittest.mock import patch
from interpreter import compile_code, tokenize_code, decompile_code, compress_code, run_interpreter
import parameters

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.temp_dir.name, "input.txt")
        # Configure logging to match runtime
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_compile_code(self):
        """Test compile_code with high-level operations."""
        lines = ["START STOP"]
        result = compile_code(lines)
        self.assertEqual(result, parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0])

    def test_compile_code_invalid(self):
        """Test compile_code with invalid operations."""
        with patch('logging.Logger.warning') as mocked_warning:
            lines = ["INVALID"]
            result = compile_code(lines)
            self.assertEqual(result, "")
            mocked_warning.assert_called_with("Skipping invalid instruction: %s", "INVALID")

    def test_tokenize_code(self):
        """Test tokenize_code splits code into codons."""
        code = "AAAAUA"
        result = tokenize_code(code)
        self.assertEqual(result, ["AAA", "AUA"])

    def test_decompile_code(self):
        """Test decompile_code converts codons to operations."""
        code = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        result = decompile_code(code)
        self.assertEqual(result, "START STOP")

    def test_compress_code(self):
        """Test compress_code keeps only operational codons."""
        code = "AAAUUUAUA"  # START, NO_OP, STOP
        result = compress_code(code)
        self.assertEqual(result, parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0])

    def test_run_interpreter_no_input(self):
        """Test run_interpreter exits on quit."""
        with patch('builtins.input', side_effect=["quit"]):
            with patch('interpreter.logging.info') as mocked_info:
                run_interpreter(verbose=False)
                mocked_info.assert_called_with("Exiting interpreter")

    def test_run_interpreter_with_input(self):
        """Test run_interpreter processes input file."""
        with open(self.input_file, 'w') as f:
            f.write("UUU\nrun\nquit\n")
        
        with patch('interpreter.logging.info') as mocked_info:
            run_interpreter(input_file=self.input_file, verbose=False)
            print("Mocked info calls:", mocked_info.call_args_list)  # Debug
            mocked_info.assert_any_call("Execution complete. Progeny code: %s", "UUU")
            mocked_info.assert_any_call("Exiting interpreter")

if __name__ == '__main__':
    unittest.main()
