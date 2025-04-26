#!/usr/bin/env python3

"""Unit tests for checks module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import parameters
import checks

class TestChecks(unittest.TestCase):
    def test_check_list_valid(self):
        """Test check_list with a valid code string."""
        valid_code = "AAAAAA"  # Two valid codons
        self.assertTrue(checks.check_list(valid_code))

    def test_check_list_invalid_codon(self):
        """Test check_list with an invalid codon."""
        invalid_code = "AAAAAF"  # 'AAF' is not in INSTRUCTIONS
        self.assertFalse(checks.check_list(invalid_code))

    def test_check_list_wrong_length(self):
        """Test check_list with a code string of incorrect length."""
        invalid_code = "AAAA"  # Length 4, not a multiple of CODON_SIZE (3)
        self.assertFalse(checks.check_list(invalid_code))

    def test_check_list_empty(self):
        """Test check_list with an empty string."""
        self.assertFalse(checks.check_list(""))

    def test_is_executable_valid(self):
        """Test is_executable with valid instruction lists."""
        for stop_codon in parameters.OPERATIONS["STOP"]:
            instructions = [parameters.OPERATIONS["START"][0], stop_codon]
            self.assertTrue(checks.is_executable(instructions), f"Failed for STOP codon {stop_codon}")

    def test_is_executable_no_stop(self):
        """Test is_executable with a START but no STOP."""
        instructions = [parameters.OPERATIONS["START"][0], parameters.OPERATIONS["START"][0]]
        self.assertFalse(checks.is_executable(instructions))

    def test_is_executable_empty(self):
        """Test is_executable with an empty instruction list."""
        self.assertFalse(checks.is_executable([]))

    def test_is_executable_no_start(self):
        """Test is_executable with a STOP but no START."""
        instructions = [parameters.OPERATIONS["STOP"][0], parameters.OPERATIONS["COPY"][0]]
        self.assertFalse(checks.is_executable(instructions))

if __name__ == '__main__':
    unittest.main()
