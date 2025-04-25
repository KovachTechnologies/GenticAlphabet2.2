#!/usr/bin/env python3

"""Verification methods for genetic programs."""

from typing import List
import parameters

def check_list(code: str) -> bool:
    """
    Verify that a genetic code string is valid.

    A valid code string must:
    - Be non-empty.
    - Have a length that is a multiple of CODON_SIZE.
    - Consist only of codons from parameters.INSTRUCTIONS.

    Args:
        code: The genetic code string to validate.

    Returns:
        True if the code is valid, False otherwise.
    """
    if not code:
        return False

    if len(code) % parameters.CODON_SIZE != 0:
        return False

    tape = [code[i:i + parameters.CODON_SIZE] for i in range(0, len(code), parameters.CODON_SIZE)]
    return all(codon in parameters.INSTRUCTIONS for codon in tape)

def is_executable(instruction_list: List[str]) -> bool:
    """
    Check if a list of instructions forms an executable program.

    An executable program must have at least one START instruction followed by
    at least one STOP instruction in the sequence.

    Args:
        instruction_list: List of codons to check.

    Returns:
        True if the program is executable, False otherwise.
    """
    if not instruction_list:
        return False

    start_found = False
    for i, instruction in enumerate(instruction_list):
        if instruction in parameters.OPERATIONS["START"]:
            start_found = True
            for j in range(i, len(instruction_list)):
                if instruction_list[j] in parameters.OPERATIONS["STOP"]:
                    return True
    return False
