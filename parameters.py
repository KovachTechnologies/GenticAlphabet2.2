#!/usr/bin/env python3

"""Global configuration parameters for the genetic simulation."""

from typing import Dict, List, Set
import sys

# Simulation limits
MAX_ITERATIONS: int = 1000
"""Maximum number of iterations for a simulation run."""
MAX_GENE_SIZE: int = 1024
"""Maximum size of a genetic sequence in codons."""
MID_GENE_SIZE: int = 10
"""Typical size for initializing genetic sequences."""
MIN_GENE_SIZE: int = 2
"""Minimum size of a genetic sequence in codons."""
MAX_PROGENY: int = 128
"""Maximum number of progeny sequences."""
MAX_PRODUCT_SIZE: int = 1024
"""Maximum size of product code."""
CODON_SIZE: int = 3
"""Size of each codon in characters."""

# Runtime configuration
DYNAMIC_MODE: bool = False
"""Enable dynamic execution mode for debugging."""
DYNAMIC_INSTRUCTIONS: int = 0
"""Counter for dynamically executed instructions."""

# Instruction set
INSTRUCTIONS: List[str] = [
    "AAA", "AAU", "AAG", "AAC", "AUA", "AUU", "AUG", "AUC",
    "AGA", "AGU", "AGG", "AGC", "ACA", "ACU", "ACG", "ACC",
    "UAA", "UAU", "UAG", "UAC", "UUA", "UUU", "UUG", "UUC",
    "UGA", "UGU", "UGG", "UGC", "UCA", "UCU", "UCG", "UCC",
    "GAA", "GAU", "GAG", "GAC", "GUA", "GUU", "GUG", "GUC",
    "GGA", "GGU", "GGG", "GGC", "GCA", "GCU", "GCG", "GCC",
    "CAA", "CAU", "CAG", "CAC", "CUA", "CUU", "CUG", "CUC",
    "CGA", "CGU", "CGG", "CGC", "CCA", "CCU", "CCG", "CCC",
    "ATC", "ATG"  # Added to support STOP codons
]
"""List of all valid codons, each of length CODON_SIZE."""

OPERATIONS: Dict[str, List[str]] = {
    "COND": ["UUC", "UUA", "GAA"],
    "COPY": ["AAG"],
    "IF": ["AAU"],
    "JUMP": ["CUU"],
    "START": ["AAA"],
    "STOP": ["AUA", "ATC", "ATG"]
}
"""Dictionary mapping operation names to their corresponding codons."""

# Derived sets for efficient lookups
NO_OPS: Set[str] = set(INSTRUCTIONS) - set(sum(OPERATIONS.values(), []))
"""Set of codons that do not correspond to any operation."""

# Validation
def validate_parameters() -> None:
    """Validate the configuration parameters to ensure consistency."""
    # Check codon size
    if CODON_SIZE != 3:
        raise ValueError(f"CODON_SIZE must be 3, got {CODON_SIZE}")

    # Check all instructions are of correct length
    for codon in INSTRUCTIONS:
        if len(codon) != CODON_SIZE:
            raise ValueError(f"Invalid codon length for {codon}, expected {CODON_SIZE}")

    # Check for duplicate codons in INSTRUCTIONS
    if len(INSTRUCTIONS) != len(set(INSTRUCTIONS)):
        raise ValueError("Duplicate codons found in INSTRUCTIONS")

    # Check all operation codons are valid
    all_op_codons = set(sum(OPERATIONS.values(), []))
    invalid_ops = all_op_codons - set(INSTRUCTIONS)
    if invalid_ops:
        raise ValueError(
            f"Operation codons not in INSTRUCTIONS: {invalid_ops}. "
            f"Check OPERATIONS dictionary for invalid codons."
        )

    # Check for overlapping operation codons
    seen_codons: Set[str] = set()
    for op, codons in OPERATIONS.items():
        for codon in codons:
            if codon in seen_codons:
                raise ValueError(f"Codon {codon} assigned to multiple operations in OPERATIONS")
            seen_codons.add(codon)

    # Check NO_OPS
    expected_no_ops = set(INSTRUCTIONS) - all_op_codons
    if NO_OPS != expected_no_ops:
        raise ValueError("NO_OPS does not match expected non-operational codons")

# Run validation on module import
validate_parameters()

if __name__ == "__main__":
    print("Configuration parameters for genetic simulation:")
    print(f"  Maximum genome size: {MAX_GENE_SIZE}")
    print(f"  Minimum genome size: {MIN_GENE_SIZE}")
    print(f"  Maximum product size: {MAX_PRODUCT_SIZE}")
    print(f"  Codon size: {CODON_SIZE}")
    print(f"  Number of instructions: {len(INSTRUCTIONS)}")
    print(f"  Number of operations: {len(OPERATIONS)}")
    print("\nFor detailed testing, run: pytest tests/test_parameters.py")
    sys.exit(0)
