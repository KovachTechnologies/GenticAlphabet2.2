#!/usr/bin/env python3

"""Unit tests for parameters module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import parameters

class TestParameters(unittest.TestCase):
    def test_simulation_limits(self):
        """Test simulation limit constants."""
        self.assertEqual(parameters.MAX_ITERATIONS, 1000)
        self.assertEqual(parameters.MAX_GENE_SIZE, 1024)
        self.assertEqual(parameters.MID_GENE_SIZE, 10)
        self.assertEqual(parameters.MIN_GENE_SIZE, 2)
        self.assertEqual(parameters.MAX_PROGENY, 128)
        self.assertEqual(parameters.MAX_PRODUCT_SIZE, 1024)
        self.assertEqual(parameters.CODON_SIZE, 3)

    def test_runtime_configuration(self):
        """Test runtime configuration defaults."""
        self.assertFalse(parameters.DYNAMIC_MODE)
        self.assertEqual(parameters.DYNAMIC_INSTRUCTIONS, 0)

    def test_instructions(self):
        """Test the INSTRUCTIONS list."""
        self.assertEqual(len(parameters.INSTRUCTIONS), 66)  # 64 original + ATC, ATG
        self.assertTrue(all(len(codon) == parameters.CODON_SIZE for codon in parameters.INSTRUCTIONS))
        self.assertEqual(len(parameters.INSTRUCTIONS), len(set(parameters.INSTRUCTIONS)))  # No duplicates
        self.assertIn("AAA", parameters.INSTRUCTIONS)
        self.assertIn("ATC", parameters.INSTRUCTIONS)
        self.assertIn("ATG", parameters.INSTRUCTIONS)

    def test_operations(self):
        """Test the OPERATIONS dictionary."""
        expected_ops = {
            "COND": ["UUC", "UUA", "GAA"],
            "COPY": ["AAG"],
            "IF": ["AAU"],
            "JUMP": ["CUU"],
            "START": ["AAA"],
            "STOP": ["AUA", "ATC", "ATG"]
        }
        self.assertEqual(parameters.OPERATIONS, expected_ops)
        all_op_codons = set(sum(parameters.OPERATIONS.values(), []))
        self.assertTrue(all(codon in parameters.INSTRUCTIONS for codon in all_op_codons))

    def test_no_ops(self):
        """Test the NO_OPS set."""
        all_op_codons = set(sum(parameters.OPERATIONS.values(), []))
        expected_no_ops = set(parameters.INSTRUCTIONS) - all_op_codons
        self.assertEqual(parameters.NO_OPS, expected_no_ops)
        self.assertEqual(len(parameters.NO_OPS), len(parameters.INSTRUCTIONS) - len(all_op_codons))

    def test_validate_parameters_codon_size(self):
        """Test validation raises error for invalid CODON_SIZE."""
        original = parameters.CODON_SIZE
        parameters.CODON_SIZE = 4
        with self.assertRaisesRegex(ValueError, "CODON_SIZE must be 3"):
            parameters.validate_parameters()
        parameters.CODON_SIZE = original

    def test_validate_parameters_duplicate_instructions(self):
        """Test validation raises error for duplicate INSTRUCTIONS."""
        original = parameters.INSTRUCTIONS
        parameters.INSTRUCTIONS = ["AAA", "AAA"]
        with self.assertRaisesRegex(ValueError, "Duplicate codons found"):
            parameters.validate_parameters()
        parameters.INSTRUCTIONS = original

    def test_validate_parameters_invalid_ops(self):
        """Test validation raises error for invalid operation codons."""
        original = parameters.OPERATIONS
        parameters.OPERATIONS["STOP"] = ["XYZ"]
        with self.assertRaisesRegex(ValueError, "Operation codons not in INSTRUCTIONS"):
            parameters.validate_parameters()
        parameters.OPERATIONS = original

if __name__ == '__main__':
    unittest.main()
