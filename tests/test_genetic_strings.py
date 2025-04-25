#!/usr/bin/env python3

"""Unit tests for genetic_strings module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import random
import parameters
from genetic_strings import entropy, create_codon, create_string, mutate

class TestGeneticStrings(unittest.TestCase):
    def setUp(self):
        """Set up a consistent random seed for reproducible tests."""
        random.seed(42)

    def test_entropy_empty(self):
        """Test entropy for an empty string."""
        self.assertEqual(entropy(""), 0.0)

    def test_entropy_single_codon(self):
        """Test entropy for a single codon."""
        result = entropy("AAA")
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_entropy_multiple_codons(self):
        """Test entropy for a string with multiple codons."""
        code = "AAAAAA"  # Two AAA codons
        result = entropy(code)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_create_codon(self):
        """Test create_codon returns a valid codon."""
        codon = create_codon()
        self.assertIn(codon, parameters.INSTRUCTIONS)
        self.assertEqual(len(codon), parameters.CODON_SIZE)

    def test_create_string(self):
        """Test create_string generates a valid string."""
        code = create_string()
        self.assertEqual(len(code) % parameters.CODON_SIZE, 0)
        self.assertGreaterEqual(len(code), parameters.MIN_GENE_SIZE * parameters.CODON_SIZE)
        self.assertLessEqual(len(code), parameters.MID_GENE_SIZE * parameters.CODON_SIZE)
        self.assertTrue(
            all(code[i:i + parameters.CODON_SIZE] in parameters.INSTRUCTIONS
                for i in range(0, len(code), parameters.CODON_SIZE))
        )

    def test_mutate_no_change(self):
        """Test mutate with a no-op mutation."""
        code = "AAAAAA"
        random.seed(7)  # No-op index
        mutated = mutate(code)
        self.assertEqual(mutated, code)

    def test_mutate_append(self):
        """Test mutate with append mutation."""
        code = "AAA"
        mutated = None
        for seed in range(1000):  # Try seeds until append occurs
            random.seed(seed)
            mutated = mutate(code)
            if len(mutated) == len(code) + parameters.CODON_SIZE and mutated.startswith(code):
                break
        else:
            self.fail(f"No append mutation found in 1000 seeds; last mutated: {mutated}")
        self.assertEqual(len(mutated), len(code) + parameters.CODON_SIZE)
        self.assertTrue(mutated.startswith(code))
        self.assertIn(mutated[-parameters.CODON_SIZE:], parameters.INSTRUCTIONS)

    def test_mutate_prepend(self):
        """Test mutate with prepend mutation."""
        code = "AAA"
        mutated = None
        for seed in range(1000):  # Try seeds until prepend occurs
            random.seed(seed)
            mutated = mutate(code)
            if len(mutated) == len(code) + parameters.CODON_SIZE and mutated.endswith(code):
                break
        else:
            self.fail(f"No prepend mutation found in 1000 seeds; last mutated: {mutated}")
        self.assertEqual(len(mutated), len(code) + parameters.CODON_SIZE)
        self.assertTrue(mutated.endswith(code))
        self.assertIn(mutated[:parameters.CODON_SIZE], parameters.INSTRUCTIONS)

    def test_mutate_reverse(self):
        """Test mutate with reverse mutation."""
        code = "AAAAAA"
        random.seed(6)  # Reverse index
        mutated = mutate(code)
        self.assertEqual(mutated, code)  # Reverse of identical codons is same

if __name__ == '__main__':
    unittest.main()
