#!/usr/bin/env python3

"""Unit tests for agent module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from agent import Agent
import parameters
import genetic_strings

class TestAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.agent = Agent(family_id=0)
        parameters.DYNAMIC_MODE = True

    def test_init_valid_code(self):
        """Test initialization with valid code."""
        self.assertTrue(self.agent.init("AAAAAA"))
        self.assertEqual(self.agent.code, "AAAAAA")
        self.assertEqual(self.agent.tape, ["AAA", "AAA"])

    def test_init_invalid_code(self):
        """Test initialization with invalid code."""
        with self.assertLogs(level='ERROR') as cm:
            self.assertFalse(self.agent.init("INVALID"))
            self.assertIn("Invalid code for agent (family_id=0): INVALID", 
                          cm.output[0])

    def test_iteration_copy(self):
        """Test iteration with COPY operation."""
        self.agent.init("AAGAAG")
        self.assertFalse(self.agent.iteration())  # First COPY
        self.assertEqual(self.agent.progeny_code, "AAG")
        self.assertFalse(self.agent.iteration())  # Second COPY
        self.assertEqual(self.agent.progeny_code, "AAGAAG")
        self.assertTrue(self.agent.iteration())  # End of code
        self.assertEqual(self.agent.progeny_code, "AAGAAG")

    def test_iteration_short_code(self):
        """Test iteration with short code."""
        self.agent.init("AAA")
        self.assertFalse(self.agent.iteration())  # START codon
        self.assertEqual(self.agent.progeny_code, "")  # START does not append to progeny_code
        self.assertEqual(self.agent.eip_ptr, 0)  # START sets eip_ptr
        self.assertTrue(self.agent.iteration())  # End of code

    def test_iteration_data_codon(self):
        """Test iteration with data codon."""
        self.agent.init("UUU")
        self.assertFalse(self.agent.iteration())  # Data codon
        self.assertEqual(self.agent.progeny_code, "UUU")
        self.assertTrue(self.agent.iteration())  # End of code

    def test_mutate(self):
        """Test mutation of code."""
        self.agent.init("AAAAAA")
        with patch('genetic_strings.mutate', return_value="AAACCC"):
            self.agent.mutate()
            self.assertEqual(self.agent.code, "AAACCC")

    def test_evaluate_fitness(self):
        """Test fitness evaluation."""
        self.agent.init("AAAAAA")
        self.agent.progeny_code = "AAAAAA"
        with patch('genetic_strings.entropy', return_value=1.0):
            fitness = self.agent.evaluate_fitness()
            self.assertEqual(fitness, 6.0)

    def test_translate_to_peptide(self):
        """Test translation of progeny_code to peptide sequence."""
        self.agent.init("UUUUUC")  # Phenylalanine codons
        self.agent.progeny_code = "UUUUUC"
        peptide = self.agent.translate_to_peptide()
        self.assertEqual(peptide, "FF")  # UUU, UUC -> Phenylalanine (F)

    def test_evaluate_fitness_with_peptide(self):
        """Test fitness evaluation with target peptide."""
        self.agent.init("UUUUUC")
        self.agent.progeny_code = "UUUUUC"  # Translates to "FF"
        with patch('genetic_strings.entropy', return_value=1.0):
            fitness = self.agent.evaluate_fitness(target_peptide="FF")
            self.assertGreater(fitness, 6.0)  # Base fitness + peptide match bonus
            fitness_no_match = self.agent.evaluate_fitness(target_peptide="GG")
            self.assertEqual(fitness_no_match, 6.0)  # Base fitness only

if __name__ == '__main__':
    unittest.main()
