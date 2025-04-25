#!/usr/bin/env python3

"""String processing and mutation operations for genetic sequences."""

from typing import List
import math
import random
import parameters

def entropy(code: str) -> float:
    """
    Calculate the entropy of a genetic code string based on codon frequencies.

    Args:
        code: The genetic code string.

    Returns:
        The entropy value, or 0.0 if the code is empty.
    """
    if not code:
        return 0.0

    tape = [code[i:i + parameters.CODON_SIZE] for i in range(0, len(code), parameters.CODON_SIZE)]
    histogram = {instr: 0 for instr in parameters.INSTRUCTIONS}
    for codon in tape:
        histogram[codon] += 1

    total = sum(histogram.values())
    if total == 0:
        return 0.0

    squared_sum = sum((count / total) ** 2 for count in histogram.values())
    return -2.0 * float(math.log(math.sqrt(squared_sum), 64))

def create_codon() -> str:
    """
    Generate a random codon from the instruction set.

    Returns:
        A randomly selected codon from parameters.INSTRUCTIONS.
    """
    return random.choice(parameters.INSTRUCTIONS)

def create_string() -> str:
    """
    Create a random genetic code string.

    The string length is randomly chosen between MIN_GENE_SIZE and MID_GENE_SIZE
    (in codons), and consists of random codons.

    Returns:
        A random genetic code string.
    """
    str_size = random.randrange(parameters.MIN_GENE_SIZE, parameters.MID_GENE_SIZE)
    return ''.join(create_codon() for _ in range(str_size))

def mutate(code: str) -> str:
    """
    Apply a random mutation to a genetic code string.

    Mutations include:
    - Append: Add a codon to the end.
    - Prepend: Add a codon to the beginning.
    - Insert: Insert a codon at a random position.
    - Rewrite: Replace a codon at a random position.
    - Remove: Delete a random codon.
    - Swap: Swap two random codons.
    - Reverse: Reverse the entire string.
    - No-op: No change (for some random choices).

    Args:
        code: The genetic code string to mutate.

    Returns:
        The mutated code string.
    """
    if not code:
        return code

    tape = [code[i:i + parameters.CODON_SIZE] for i in range(0, len(code), parameters.CODON_SIZE)]
    mutation_index = random.choice(range(10))  # 0-9, some are no-ops

    if mutation_index == 0 and len(tape) + 1 <= parameters.MAX_GENE_SIZE:
        tape.append(create_codon())  # Append
    elif mutation_index == 1 and len(tape) + 1 <= parameters.MAX_GENE_SIZE:
        tape.insert(0, create_codon())  # Prepend
    elif mutation_index == 2 and len(tape) + 1 <= parameters.MAX_GENE_SIZE:
        tape.insert(random.randrange(0, len(tape)), create_codon())  # Insert
    elif mutation_index == 3 and tape:
        tape[random.randrange(0, len(tape))] = create_codon()  # Rewrite
    elif mutation_index == 4 and len(tape) > parameters.MIN_GENE_SIZE:
        tape.pop(random.randrange(0, len(tape)))  # Remove
    elif mutation_index == 5 and len(tape) >= 2:
        idx1, idx2 = random.sample(range(len(tape)), 2)
        tape[idx1], tape[idx2] = tape[idx2], tape[idx1]  # Swap
    elif mutation_index == 6:
        tape.reverse()  # Reverse

    return ''.join(tape)
