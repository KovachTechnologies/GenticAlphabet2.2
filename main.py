#!/usr/bin/env python3

"""Command-line entry point for running genetic simulations and interactive interpreter."""

import argparse
import sys
import logging
from typing import Optional, List
from pathlib import Path
import parameters
import checks
import genetic_strings
from simulation import Simulation
from interpreter import compile_code, decompile_code, compress_code

# Configure logging
def setup_logging(log_file: Optional[str] = None, verbose: bool = False) -> None:
    """
    Configure logging with console and optional file handlers.

    Args:
        log_file: Path to log file, or None for console-only.
        verbose: If True, enable DEBUG level; otherwise, INFO.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logging.getLogger().addHandler(file_handler)

def load_input_file(file_path: str, should_compile: bool = False) -> List[str]:
    """
    Load genetic codes from an input file, ignoring comments.

    Comments are lines starting with '#' (after stripping whitespace) and are ignored.
    If should_compile is True, lines are treated as uncompiled operations (e.g., 'START STOP')
    or NO_OP codons and compiled to codons. Otherwise, lines must be valid codon sequences.

    Args:
        file_path: Path to the input file.
        should_compile: If True, compile uncompiled code to codons.

    Returns:
        List of valid genetic code strings (compiled codons).

    Raises:
        ValueError: If the file contains invalid codes or cannot be read.
    """
    try:
        with open(file_path, 'r') as f:
            codes = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except IOError as e:
        logging.error("Failed to read input file %s: %s", file_path, e)
        raise ValueError(f"Failed to read input file {file_path}: {e}")

    valid_codes = []
    for code in codes:
        if should_compile:
            try:
                code = compile_code(code)  # Compile uncompiled code to codons
            except ValueError as e:
                logging.error("Failed to compile code in %s: %s (%s)", file_path, code, e)
                raise ValueError(f"Failed to compile code in {file_path}: {code} ({e})")
        if checks.check_list(code):
            valid_codes.append(code)
        else:
            logging.error("Invalid genetic code in %s: %s", file_path, code)
            raise ValueError(f"Invalid genetic code in {file_path}: {code}")
    
    if not valid_codes:
        logging.error("No valid genetic codes found in %s", file_path)
        raise ValueError(f"No valid genetic codes found in {file_path}")
    
    return valid_codes

def write_output_file(file_path: str, run_number: int, best_agent: Optional['Agent'], simulation: 'Simulation') -> None:
    """
    Write simulation results to an output file.

    Args:
        file_path: Path to the output file.
        run_number: Current simulation run number.
        best_agent: Best agent from the simulation (or None if empty).
        simulation: The simulation instance.
    """
    cumulative_entropy = sum(genetic_strings.entropy(agent.progeny_code or agent.code) 
                            for agent in simulation.population)
    mode = 'a' if Path(file_path).exists() else 'w'
    try:
        with open(file_path, mode) as f:
            f.write(f"Run {run_number}:\n")
            f.write(f"Cumulative Entropy: {cumulative_entropy:.3f}\n")
            if best_agent:
                f.write(f"Best Code: {best_agent.code}\n")
            else:
                f.write("Best Code: None (empty population)\n")
            f.write("\n")
        logging.info("Wrote simulation results to %s", file_path)
    except IOError as e:
        logging.error("Failed to write output file %s: %s", file_path, e)
        raise

def run_simulation(population_size: int, generations: int, max_steps: int, max_runs: int, 
                   input_file: Optional[str], output_file: Optional[str], verbose: bool, 
                   should_compile: bool = False) -> None:
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
                         max_steps=max_steps, initial_codes=initial_codes)
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

def run_interpreter() -> None:
    """
    Run an interactive interpreter for compiling and decompiling genetic code.

    Commands:
        compile <code>: Compile high-level code to codons.
        decompile <code>: Decompile codons to high-level code.
        compress <code>: Compress code by removing NO_OPs.
        quit: Exit the interpreter.
    """
    logging.info("Starting Genetic Code Interpreter (type 'quit' to exit)")
    logging.info("Commands: compile <code>, decompile <code>, compress <code>")
    while True:
        try:
            command = input("> ").strip()
            logging.debug("Received command: %s", command)
            if command.lower() == "quit":
                logging.info("Exiting interpreter")
                break
            if not command:
                continue

            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                logging.error("Command requires an argument (e.g., 'compile START STOP')")
                continue

            cmd, code = parts[0].lower(), parts[1]
            if cmd == "compile":
                try:
                    result = compile_code(code)
                    logging.info("Compiled: %s", result)
                except ValueError as e:
                    logging.error("Compilation error: %s", e)
            elif cmd == "decompile":
                try:
                    result = decompile_code(code)
                    logging.info("Decompiled: %s", result)
                except ValueError as e:
                    logging.error("Decompilation error: %s", e)
            elif cmd == "compress":
                try:
                    result = compress_code(code)
                    logging.info("Compressed: %s", result)
                except ValueError as e:
                    logging.error("Compression error: %s", e)
            else:
                logging.error("Unknown command: %s. Use compile, decompile, or compress.", cmd)

        except KeyboardInterrupt:
            logging.info("Exiting interpreter via KeyboardInterrupt")
            break
        except Exception as e:
            logging.error("Interpreter error: %s", e)

def main() -> None:
    """Parse command-line arguments and run the specified mode."""
    parser = argparse.ArgumentParser(description="Genetic Alphabet Simulator and Interpreter")
    parser.add_argument(
        "--mode",
        choices=["simulation", "interpreter"],
        default="simulation",
        help="Mode to run: simulation or interpreter (default: simulation)"
    )
    parser.add_argument(
        "--population",
        type=int,
        default=50,
        help=f"Population size (max {parameters.MAX_PROGENY}, default: 50)"
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=100,
        help=f"Number of generations per run (max {parameters.MAX_ITERATIONS}, default: 100)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=parameters.MAX_ITERATIONS,
        help=f"Max execution steps per agent (default: {parameters.MAX_ITERATIONS})"
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=1,
        help="Number of simulation runs (default: 1)"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to input file with initial genetic codes"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to output file for simulation results"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file for detailed output (default: console only)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (sets DYNAMIC_MODE and DEBUG logging)"
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile input file codes as high-level operations before use (simulation mode only)"
    )

    args = parser.parse_args()

    # Setup logging before any operations
    setup_logging(log_file=args.log_file, verbose=args.verbose)

    if args.mode == "simulation":
        run_simulation(
            population_size=args.population,
            generations=args.generations,
            max_steps=args.max_steps,
            max_runs=args.max_runs,
            input_file=args.input_file,
            output_file=args.output_file,
            verbose=args.verbose,
            should_compile=args.compile
        )
    else:  # interpreter
        run_interpreter()

if __name__ == '__main__':
    main()
