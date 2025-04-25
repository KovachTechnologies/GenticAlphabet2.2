#!/usr/bin/env python3

"""Unit tests for main module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, mock_open
import tempfile
import logging
import parameters
from main import load_input_file, write_output_file, run_simulation, run_interpreter, setup_logging
from simulation import Simulation
from interpreter import compile_code

class TestMain(unittest.TestCase):
    def setUp(self):
        """Set up temporary files and simulation parameters."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.temp_dir.name, "input.txt")
        self.output_file = os.path.join(self.temp_dir.name, "output.txt")
        self.valid_codes = ["AAAAAA", "AAAATC"]
        self.valid_ops = ["START STOP", "COPY STOP"]
        # Setup logging to capture output
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.log_capture = []
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.DEBUG)
        self.handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        self.logger.addHandler(self.handler)

    def tearDown(self):
        """Clean up temporary directory and logging."""
        self.logger.removeHandler(self.handler)
        self.temp_dir.cleanup()

    def test_load_input_file_valid(self):
        """Test load_input_file with valid genetic codes."""
        with open(self.input_file, 'w') as f:
            f.write("\n".join(self.valid_codes))
        codes = load_input_file(self.input_file, should_compile=False)
        self.assertEqual(codes, self.valid_codes)

    def test_load_input_file_with_comments(self):
        """Test load_input_file with comments."""
        input_content = "# Comment line\nAAAAAA\n# Another comment\nAAAATC\n"
        with open(self.input_file, 'w') as f:
            f.write(input_content)
        codes = load_input_file(self.input_file, should_compile=False)
        self.assertEqual(codes, self.valid_codes)

    def test_load_input_file_uncompiled(self):
        """Test load_input_file with uncompiled operations and --compile."""
        input_content = "# Comment line\nSTART STOP\nCOPY STOP\n"
        with open(self.input_file, 'w') as f:
            f.write(input_content)
        expected_codes = [compile_code(op) for op in self.valid_ops]
        codes = load_input_file(self.input_file, should_compile=True)
        self.assertEqual(codes, expected_codes)

    def test_load_input_file_invalid(self):
        """Test load_input_file with invalid genetic code."""
        with open(self.input_file, 'w') as f:
            f.write("AAAA\nAAAAAA")
        with self.assertRaisesRegex(ValueError, "Invalid genetic code"):
            load_input_file(self.input_file, should_compile=False)

    def test_load_input_file_empty(self):
        """Test load_input_file with empty file."""
        with open(self.input_file, 'w') as f:
            f.write("")
        with self.assertRaisesRegex(ValueError, "No valid genetic codes"):
            load_input_file(self.input_file, should_compile=False)

    def test_write_output_file(self):
        """Test write_output_file saves correct results."""
        sim = Simulation(population_size=2, max_generations=1, max_steps=100, initial_codes=self.valid_codes)
        best_agent = sim.run_simulation()
        write_output_file(self.output_file, 1, best_agent, sim)
        with open(self.output_file, 'r') as f:
            content = f.read()
        self.assertIn("Run 1:", content)
        self.assertIn("Cumulative Entropy:", content)
        self.assertIn("Best Code:", content)

    def test_run_simulation_default(self):
        """Test run_simulation with default settings."""
        with patch('logging.Logger.info') as mocked_info:
            run_simulation(population_size=10, generations=1, max_steps=100, max_runs=1, 
                           input_file=None, output_file=None, verbose=False, should_compile=False)
            self.assertTrue(mocked_info.called)
            mocked_info.assert_any_call("Running simulation %d/%d...", 1, 1)

    def test_run_simulation_with_input_output(self):
        """Test run_simulation with input and output files."""
        with open(self.input_file, 'w') as f:
            f.write("\n".join(self.valid_codes))
        with patch('logging.Logger.info') as mocked_info:
            run_simulation(population_size=2, generations=1, max_steps=100, max_runs=1, 
                           input_file=self.input_file, output_file=self.output_file, 
                           verbose=False, should_compile=False)
            self.assertTrue(mocked_info.called)
            self.assertTrue(os.path.exists(self.output_file))
        with open(self.output_file, 'r') as f:
            content = f.read()
        self.assertIn("Run 1:", content)

    @patch('builtins.input', side_effect=['compile START STOP', 'decompile AAAAUA', 'compress AAAUUUAUA', 'quit'])
    @patch('logging.Logger.info')
    def test_run_interpreter(self, mocked_info, mocked_input):
        """Test run_interpreter handles commands correctly."""
        run_interpreter()
        mocked_info.assert_any_call("Compiled: %s", "AAAAUA")
        mocked_info.assert_any_call("Decompiled: %s", "START STOP")
        mocked_info.assert_any_call("Compressed: %s", "AAAAUA")

if __name__ == '__main__':
    unittest.main()
