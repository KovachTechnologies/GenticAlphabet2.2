#!/usr/bin/env python3

"""Agent class for genetic simulations in GeneticAlphabet2.2."""

import logging
import random
import parameters
import genetic_strings
from typing import Optional, List

class Agent:
    def __init__(self, family_id: int):
        """
        Initialize an agent with a unique family ID.

        Args:
            family_id: Unique identifier for the agent's family.
        """
        self.family_id = family_id
        self.code: str = ""
        self.progeny_code: str = ""
        self.program_counter: int = 0
        self.eip_ptr: Optional[int] = None
        self.valid: bool = False
        self.tape: List[str] = []

    def init(self, code: str, progeny_code: Optional[str] = None) -> bool:
        """
        Initialize the agent with genetic code.

        Args:
            code: Genetic code string (sequence of codons).
            progeny_code: Optional initial progeny code.

        Returns:
            True if initialization is successful, False otherwise.
        """
        # Allow short codes (at least one codon)
        if not code or len(code) < parameters.CODON_SIZE or len(code) % parameters.CODON_SIZE != 0:
            logging.error("Invalid code for agent (family_id=%d): %s", self.family_id, code)
            return False

        # Tokenize code into codons
        self.tape = [code[i:i + parameters.CODON_SIZE] 
                     for i in range(0, len(code), parameters.CODON_SIZE)]
        
        # Validate codons (operations or valid nucleotides)
        self.valid = len(self.tape) > 0 and all(
            codon in sum(parameters.OPERATIONS.values(), []) or 
            all(c in 'ATGCU' for c in codon) 
            for codon in self.tape
        )
        
        if not self.valid:
            logging.error("Invalid code for agent (family_id=%d): %s", self.family_id, code)
            return False

        self.code = code
        self.progeny_code = progeny_code or ""
        self.program_counter = 0
        self.eip_ptr = None
        logging.debug("Agent (family_id=%d) initialized with code: %s", self.family_id, code)
        return True

    def iteration(self) -> bool:
        """
        Execute one iteration of the agent's genetic code.

        Returns:
            True if execution is complete, False if more iterations are needed.
        """
        if not self.valid or self.program_counter >= len(self.tape):
            logging.debug("Execution complete for agent (family_id=%d): progeny_code=%s, PC=%d", 
                          self.family_id, self.progeny_code, self.program_counter)
            return True

        codon = self.tape[self.program_counter]
        logging.debug("Processing codon: %s at PC=%d", codon, self.program_counter)
        
        # Handle operations
        if codon in parameters.OPERATIONS["COPY"]:
            self.progeny_code += codon
            self.program_counter += 1
            logging.debug("COPY: Added %s to progeny_code", codon)
        elif codon in parameters.OPERATIONS["START"]:
            self.eip_ptr = self.program_counter
            self.program_counter += 1
            logging.debug("START: Set eip_ptr to %d", self.eip_ptr)
        elif codon in parameters.OPERATIONS["STOP"]:
            self.program_counter += 1
            logging.debug("STOP: Execution complete")
            return True
        else:
            # Treat unrecognized codons as data
            self.progeny_code += codon
            self.program_counter += 1
            logging.debug("DATA: Added %s to progeny_code", codon)

        if parameters.DYNAMIC_MODE:
            logging.debug("progeny_code=%s, program_counter=%d", 
                          self.progeny_code, self.program_counter)
        return False

    def mutate(self) -> None:
        """
        Mutate the agent's code using genetic_strings.mutate.
        """
        if not self.code:
            logging.warning("Attempted to mutate empty code for agent (family_id=%d)", 
                            self.family_id)
            return
        self.code = genetic_strings.mutate(self.code)
        # Reinitialize to validate mutated code
        self.init(self.code, self.progeny_code)

    def translate_to_peptide(self) -> str:
        """
        Translate the agent's progeny_code to an amino acid sequence.

        Returns:
            Amino acid sequence as a string.
        """
        from cross_reference import CODON_TABLE  # Import locally to avoid circular imports
        if not self.progeny_code:
            return ""
        tape = [self.progeny_code[i:i + parameters.CODON_SIZE] 
                for i in range(0, len(self.progeny_code), parameters.CODON_SIZE)]
        amino_acids = ""
        for codon in tape:
            if codon in CODON_TABLE and "letter" in CODON_TABLE[codon]:
                amino_acids += CODON_TABLE[codon]["letter"]
        return amino_acids

    def evaluate_fitness(self, target_peptide: Optional[str] = None) -> float:
        """
        Evaluate the fitness of the agent's progeny code.

        Args:
            target_peptide: Optional target peptide sequence to search for.

        Returns:
            Fitness score, combining entropy and peptide match score.
        """
        if not self.progeny_code:
            return 0.0
        entropy = genetic_strings.entropy(self.progeny_code)
        base_fitness = len(self.progeny_code) * entropy
        
        if target_peptide:
            peptide = self.translate_to_peptide()
            # Increase weight of peptide match to prioritize correct peptides
            match_score = 1.0 if target_peptide in peptide else 0.0
            base_fitness += match_score * len(target_peptide) * 100.0  # Heavily weight peptide match
            logging.debug("Peptide match for agent (family_id=%d): %s in %s, score=%.2f", 
                          self.family_id, target_peptide, peptide, match_score)
        
        return base_fitness

    def generate_random_code(self, length: int = 30) -> str:
        """
        Generate a random genetic code.

        Args:
            length: Length of the code (default: 30).

        Returns:
            Random genetic code string.
        """
        nucleotides = 'ATGCU'
        return ''.join(random.choice(nucleotides) for _ in range(length))

    def reset(self) -> None:
        """
        Reset the agent's state.
        """
        self.code = ""
        self.progeny_code = ""
        self.program_counter = 0
        self.eip_ptr = None
        self.valid = False
        self.tape = []

if __name__ == "__main__":
    import unittest
    from unittest.mock import patch

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

    unittest.main()
