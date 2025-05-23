#!/usr/bin/env python3

"""Unit tests for main module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import logging
from unittest.mock import patch
from main import load_input_file, write_output_file, run_simulation, run_interpreter
from simulation import Simulation
from agent import Agent
import parameters

class TestMain(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.temp_dir.name, "input.txt")
        self.output_file = os.path.join(self.temp_dir.name, "output.txt")
        # Configure logging to match runtime
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        logging.getLogger().setLevel(logging.CRITICAL)  # Suppress logging during tests

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_load_input_file(self):
        """Test load_input_file reads and compiles codes by default."""
        with open(self.input_file, 'w') as f:
            f.write("START COPY STOP\n# Comment\nAAA\n")
        
        # Test with default compilation
        codes = load_input_file(self.input_file)
        expected = [parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["COPY"][0] + 
                    parameters.OPERATIONS["STOP"][0], "AAA"]
        self.assertEqual(codes, expected)
        
        # Test without compilation
        codes = load_input_file(self.input_file, should_compile=False)
        self.assertEqual(codes, ["START COPY STOP", "AAA"])

    def test_load_input_file_nonexistent(self):
        """Test load_input_file handles nonexistent file."""
        codes = load_input_file("nonexistent.txt")
        self.assertEqual(codes, [])

    def test_write_output_file(self):
        """Test write_output_file saves correct results."""
        sim = Simulation(population_size=2, max_generations=1, max_steps=100, 
                         initial_codes=["AAAAAA"])
        best_agent = sim.run_simulation()
        
        write_output_file(self.output_file, 1, best_agent, sim)
        with open(self.output_file, 'r') as f:
            content = f.read()
        self.assertIn("Run 1", content)
        if best_agent:
            self.assertIn(f"family_id={best_agent.family_id}", content)
            self.assertIn(f"Code: {best_agent.code}", content)

    def test_write_output_file_no_agent(self):
        """Test write_output_file handles no valid agents."""
        sim = Simulation(population_size=0, max_generations=1, max_steps=100)
        write_output_file(self.output_file, 1, None, sim)
        with open(self.output_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Run 1: No valid agents\n")

    def test_run_simulation_default(self):
        """Test run_simulation with default settings."""
        with patch('logging.Logger.info') as mocked_info:
            run_simulation(population_size=10, generations=1, max_steps=100, max_runs=1,
                           input_file=None, output_file=None, verbose=False)
            self.assertTrue(mocked_info.called)

    def test_run_simulation_with_input_output(self):
        """Test run_simulation with input and output files."""
        with open(self.input_file, 'w') as f:
            f.write("AAAAAA\nAAAATC")
        
        with patch('logging.Logger.info') as mocked_info:
            run_simulation(population_size=2, generations=1, max_steps=100, max_runs=1,
                           input_file=self.input_file, output_file=self.output_file, 
                           verbose=False, should_compile=True)
            self.assertTrue(mocked_info.called)
        
        with open(self.output_file, 'r') as f:
            content = f.read()
        self.assertIn("Run 1", content)

    def test_run_interpreter_no_input(self):
        """Test run_interpreter without input file."""
        with patch('builtins.input', side_effect=["quit"]):
            with patch('interpreter.logging.info') as mocked_info:
                run_interpreter(verbose=False)
                mocked_info.assert_called_with("Exiting interpreter")

    def test_run_interpreter_with_input(self):
        """Test run_interpreter with input file."""
        with open(self.input_file, 'w') as f:
            f.write("UUU\nrun\nquit\n")
        
        with patch('interpreter.logging.info') as mocked_info:
            run_interpreter(input_file=self.input_file, verbose=False)
            print("Mocked info calls in test_main:", mocked_info.call_args_list)  # Debug
            mocked_info.assert_any_call("Execution complete. Progeny code: %s", "UUU")
            mocked_info.assert_any_call("Exiting interpreter")

if __name__ == '__main__':
    unittest.main()
