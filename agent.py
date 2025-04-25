#!/usr/bin/env python3

"""Agent for executing genetic code as a Turing machine."""

import logging
import parameters
import checks
from typing import Optional, List

class Agent:
    def __init__(self, family_id: int):
        """
        Initialize an agent with a family ID.

        Args:
            family_id: Unique identifier for the agent's family.
        """
        self.family_id = family_id
        self.code: str = ""  # Original code string
        self.tape: List[str] = []  # List of codons
        self.progeny_code: str = ""
        self.program_counter: int = 0  # 0-based index into tape
        self.memory: dict = {}
        self.maximum_iterations: float = float('inf')
        self.iterations: int = 0

    def init(self, code: str) -> bool:
        """
        Initialize the agent with a genetic code.

        Args:
            code: The genetic code to execute (concatenated codons).

        Returns:
            True if initialization is successful, False otherwise.
        """
        if not checks.check_list(code):
            logging.error("Invalid code for agent (family_id=%d): %s", self.family_id, code)
            return False
        
        # Split code into codons (3 bases each)
        if len(code) % parameters.CODON_SIZE != 0:
            logging.error("Code length not divisible by CODON_SIZE for agent (family_id=%d): %s", 
                          self.family_id, code)
            return False
        self.code = code
        self.tape = [code[i:i + parameters.CODON_SIZE] for i in range(0, len(code), parameters.CODON_SIZE)]
        self.progeny_code = ""
        self.program_counter = 0
        self.memory = {}
        self.iterations = 0
        if parameters.DYNAMIC_MODE:
            logging.debug("Agent (family_id=%d) initialized with tape: %s", self.family_id, self.tape)
        return True

    def set_code(self, code: str) -> bool:
        """
        Set the agent's code (wrapper for init).

        Args:
            code: The genetic code to set.

        Returns:
            True if successful, False otherwise.
        """
        return self.init(code)

    def get_instruction_pointer(self) -> Optional[int]:
        """
        Get the current program counter.

        Returns:
            The current program counter (0-based), or None if invalid.
        """
        if 0 <= self.program_counter < len(self.tape):
            return self.program_counter
        return None

    def iteration(self) -> bool:
        """
        Execute one iteration of the genetic code.

        Returns:
            True if execution is complete, False if more iterations are needed.
        """
        if self.iterations >= self.maximum_iterations:
            logging.debug("Agent (family_id=%d) reached maximum iterations: %d", 
                          self.family_id, self.maximum_iterations)
            return True

        if not self.tape or self.program_counter < 0 or self.program_counter >= len(self.tape):
            logging.error("Invalid program counter for agent (family_id=%d): %d", 
                          self.family_id, self.program_counter)
            return True

        codon = self.tape[self.program_counter]
        if parameters.DYNAMIC_MODE:
            logging.debug("Agent (family_id=%d) executing codon %s at position %d", 
                          self.family_id, codon, self.program_counter)

        # Handle operations
        if codon in parameters.OPERATIONS.get("STOP", []):
            logging.debug("Agent (family_id=%d) stopped at codon %s", self.family_id, codon)
            return True
        elif codon in parameters.OPERATIONS.get("START", []):
            self.progeny_code += codon  # Append START codon
            self.program_counter += 1
        elif codon in parameters.OPERATIONS.get("COPY", []):
            # Copy the next codon (if available) and skip it
            if self.program_counter + 1 < len(self.tape):
                self.progeny_code += self.tape[self.program_counter + 1]
                self.program_counter += 2  # Skip the copied codon
            else:
                self.program_counter += 1
        elif codon in parameters.OPERATIONS.get("JUMP", []):
            # Jump to the next occurrence of START (AAA) after current position
            for i in range(self.program_counter + 1, len(self.tape)):
                if self.tape[i] in parameters.OPERATIONS.get("START", []):
                    self.program_counter = i
                    break
            else:
                self.program_counter += 1  # No START found, move to next
        elif codon in parameters.OPERATIONS.get("COND", []):
            # Example: COND sets a memory condition
            self.memory["condition"] = True
            self.program_counter += 1
        elif codon in parameters.OPERATIONS.get("IF", []):
            # Execute next codon if condition is True, else skip
            if self.memory.get("condition", False) and self.program_counter + 1 < len(self.tape):
                self.progeny_code += self.tape[self.program_counter + 1]
                self.program_counter += 2
            else:
                self.program_counter += 2
        else:
            # NO_OP or data: append to progeny_code
            self.progeny_code += codon
            self.program_counter += 1

        self.iterations += 1
        return False
