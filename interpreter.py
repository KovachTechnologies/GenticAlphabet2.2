#!/usr/bin/env python3

"""Interpreter for compiling, tokenizing, and decompiling genetic code sequences."""

from typing import List, Dict, Optional
import parameters
import checks

def compile_code(high_level_code: str) -> str:
    """
    Compile a high-level genetic code string into a codon sequence.

    The high-level code is a space-separated string of operation names (e.g., 'START STOP')
    or codons (e.g., 'UUU', 'CCC'). Operations are mapped to codons from parameters.OPERATIONS;
    other valid codons are treated as NO_OPs and included as-is.

    Args:
        high_level_code: Space-separated string of operation names or codons.

    Returns:
        A string of concatenated codons representing the compiled code.

    Raises:
        ValueError: If a token is neither a known operation nor a valid codon.
    """
    if not high_level_code:
        return ""

    tokens = high_level_code.strip().split()
    compiled_code = ""
    for token in tokens:
        if token in parameters.OPERATIONS:
            # Map known operation to its first codon
            compiled_code += parameters.OPERATIONS[token][0]
        elif checks.check_list(token):
            # Treat valid codon as NO_OP, include as-is
            compiled_code += token
        else:
            raise ValueError(f"Invalid token: {token}. Must be a known operation or a valid codon (3 chars, A/T/G/C).")
    return compiled_code

def tokenize_code(code: str) -> List[str]:
    """
    Tokenize a genetic code string into a list of codons.

    Args:
        code: The genetic code string to tokenize.

    Returns:
        A list of codons, each of length parameters.CODON_SIZE.

    Raises:
        ValueError: If the code length is not a multiple of CODON_SIZE.
    """
    if not code:
        return []

    if len(code) % parameters.CODON_SIZE != 0:
        raise ValueError(f"Code length {len(code)} is not a multiple of CODON_SIZE {parameters.CODON_SIZE}")

    return [code[i:i + parameters.CODON_SIZE] for i in range(0, len(code), parameters.CODON_SIZE)]

def decompile_code(code: str) -> str:
    """
    Decompile a codon sequence into a high-level operation string.

    Each codon is mapped to its corresponding operation name from parameters.OPERATIONS.
    If a codon is not an operation, it’s labeled as its raw codon value (e.g., 'UUU').

    Args:
        code: The genetic code string to decompile.

    Returns:
        A space-separated string of operation names or codon values for non-operation codons.
    """
    tokens = tokenize_code(code)
    operations = []
    for codon in tokens:
        found = False
        for op_name, codons in parameters.OPERATIONS.items():
            if codon in codons:
                operations.append(op_name)
                found = True
                break
        if not found:
            operations.append(codon)  # Use codon as-is for NO_OP
    return " ".join(operations)

def compress_code(code: str) -> str:
    """
    Compress a genetic code string by removing redundant NO_OP codons.

    Only keeps codons that are in parameters.OPERATIONS; others are considered NO_OPs.

    Args:
        code: The genetic code string to compress.

    Returns:
        A compressed code string containing only operation codons.
    """
    tokens = tokenize_code(code)
    compressed_tokens = [
        token for token in tokens
        if any(token in codons for codons in parameters.OPERATIONS.values())
    ]
    return "".join(compressed_tokens)
