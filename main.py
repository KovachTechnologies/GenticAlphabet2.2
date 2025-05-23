#!/usr/bin/env python3

"""Main entry point for GeneticAlphabet2.2 framework."""

import argparse
import logging
import os
import sys
from typing import Optional, List
import parameters
from interpreter import run_interpreter, compile_code
from simulation import Simulation
import cross_reference

def load_input_file(filepath: str, should_compile: bool = True) -> List[str]:
    """
    Load genetic codes from an input file.

    Args:
        filepath: Path to the input file.
        should_compile: If True, compile the codes before returning (default: True).

    Returns:
        List of genetic codes.
    """
    if not os.path.exists(filepath):
        logging.error("Input file does not exist: %s", filepath)
        return []
    
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if should_compile:
        compiled_codes = []
        for line in lines:
            code = line.upper()
            if code in parameters.OPERATIONS:
                compiled_codes.append(parameters.OPERATIONS[code][0])
            else:
                # Split into codons and compile if necessary
                codons = [code[i:i + parameters.CODON_SIZE] 
                          for i in range(0, len(code), parameters.CODON_SIZE)]
                if all(codon in sum(parameters.OPERATIONS.values(), []) or 
                       (len(codon) == parameters.CODON_SIZE and all(c in 'ATGCU' for c in codon)) 
                       for codon in codons):
                    compiled_codes.append(code)
                else:
                    # Treat as high-level ops
                    compiled_codes.append(compile_code([code]))
        return compiled_codes
    return lines

def write_output_file(filepath: str, run_number: int, best_agent: Optional['Agent'], sim: 'Simulation') -> None:
    """
    Write simulation results to an output file.

    Args:
        filepath: Path to the output file.
        run_number: Current simulation run number.
        best_agent: Best agent from the simulation.
        sim: Simulation instance.
    """
    with open(filepath, 'a') as f:
        if best_agent:
            fitness = sim.evaluate_fitness(best_agent)
            f.write(f"Run {run_number}, Generation {sim.generation}, "
                    f"Best Agent (family_id={best_agent.family_id}), "
                    f"Fitness: {fitness:.3f}, Code: {best_agent.code}, "
                    f"Progeny Code: {best_agent.progeny_code}\n")
        else:
            f.write(f"Run {run_number}: No valid agents\n")

def run_simulation(population_size: int, generations: int, max_steps: int, max_runs: int, 
                   input_file: Optional[str], output_file: Optional[str], verbose: bool, 
                   should_compile: bool = True, target_peptide: Optional[str] = None) -> None:
    """
    Run genetic simulations with the specified parameters.

    Args:
        population_size: Number of agents in the population.
        generations: Number of generations per run.
        max_steps: Maximum execution steps per agent.
        max_runs: Number of simulation runs.
        input_file: Optional path to input file with initial codes.
        output_file: Optional path to output file for results.
        verbose: If True, enable DYNAMIC_MODE for detailed output.
        should_compile: If True, compile input file codes before use.
        target_peptide: Optional target peptide sequence to search for.
    """
    parameters.DYNAMIC_MODE = verbose
    population_size = min(population_size, parameters.MAX_PROGENY)
    generations = min(generations, parameters.MAX_ITERATIONS)
    max_steps = min(max_steps, parameters.MAX_ITERATIONS)
    max_runs = max(max_runs, 1)

    # Load initial codes if provided
    initial_codes = None
    if input_file:
        logging.info("Loading initial codes from %s%s", input_file, " with compilation" if should_compile else "")
        initial_codes = load_input_file(input_file, should_compile=should_compile)

    for run in range(1, max_runs + 1):
        logging.info("Running simulation %d/%d...", run, max_runs)
        sim = Simulation(population_size=population_size, max_generations=generations, 
                         max_steps=max_steps, initial_codes=initial_codes, max_attempts=100,
                         target_peptide=target_peptide)
        best_agent = sim.run_simulation()

        # Log results
        if best_agent:
            logging.info("Run %d completed after %d generations", run, sim.generation)
            logging.info("Best agent (family_id=%d):", best_agent.family_id)
            logging.info("  Code: %s", best_agent.code)
            logging.info("  Progeny code: %s", best_agent.progeny_code)
            logging.info("  Fitness: %.3f", sim.evaluate_fitness(best_agent))
        else:
            logging.warning("Run %d failed: No agents in population", run)

        # Write to output file if specified
        if output_file:
            write_output_file(output_file, run, best_agent, sim)

def main():
    """Main function to parse arguments and run the framework."""
    parser = argparse.ArgumentParser(description="GeneticAlphabet2.2 Framework")
    parser.add_argument("--mode", choices=["simulation", "interpreter", "cross-reference"], 
                        default="simulation", help="Operation mode")
    parser.add_argument("--input-file", type=str, help="Input file with initial codes or commands")
    parser.add_argument("--output-file", type=str, help="Output file for results")
    parser.add_argument("--log-file", type=str, default="genetic_alphabet.log", 
                        help="Log file path")
    parser.add_argument("--population-size", type=int, default=10, 
                        help="Population size for simulation")
    parser.add_argument("--generations", type=int, default=100, 
                        help="Number of generations for simulation")
    parser.add_argument("--max-steps", type=int, default=100, 
                        help="Maximum execution steps per agent")
    parser.add_argument("--max-runs", type=int, default=1, 
                        help="Number of simulation runs")
    parser.add_argument("--num-random", type=int, default=100, 
                        help="Number of random sequences for cross-reference")
    parser.add_argument("--verbose", action="store_true", 
                        help="Enable verbose logging (DYNAMIC_MODE)")
    parser.add_argument("--compile", action="store_true", 
                        help="Compile input file codes before simulation")
    parser.add_argument("--target-peptide", type=str, help="Target peptide sequence to search for")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(filename=args.log_file, level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

    if args.mode == "simulation":
        run_simulation(args.population_size, args.generations, args.max_steps, 
                       args.max_runs, args.input_file, args.output_file, 
                       args.verbose, args.compile, args.target_peptide)
    elif args.mode == "interpreter":
        run_interpreter(args.input_file, args.verbose)
    elif args.mode == "cross-reference":
        initial_codes = None
        if args.input_file:
            initial_codes = load_input_file(args.input_file, args.compile)
        cross_reference.run_cross_reference(
            population_size=args.population_size,
            max_generations=args.generations,
            max_steps=args.max_steps,
            num_random=args.num_random,
            initial_codes=initial_codes,
            output_prefix="cross_reference",
            target_peptide=args.target_peptide
        )

if __name__ == "__main__":
    main()
