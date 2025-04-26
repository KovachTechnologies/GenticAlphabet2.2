# GeneticAlphabet2.1

A Python-based genetic programming framework for simulating and editing genetic code sequences, featuring a command-line interface (CLI) and a PyQt5 graphical user interface (GUI).

## Overview

GeneticAlphabet2.1 is a versatile tool for exploring genetic algorithms and Turing machine-based code execution. It allows users to:
- Generate, mutate, and evolve genetic code sequences.
- Compile and decompile high-level instructions to/from codon sequences.
- Simulate populations of agents to optimize genetic code.
- Visualize and interactively edit code execution via a GUI.

Key components include:
- **Core Modules**:
  - `agent.py`: Executes genetic code as a Turing machine, producing `progeny_code`.
  - `genetic_strings.py`: Generates and mutates genetic code sequences.
  - `interpreter.py`: Compiles/decompiles code and compresses NO_OP codons.
  - `simulation.py`: Evolves populations of agents using genetic algorithms.
- **Interfaces**:
  - `main.py`: CLI for running simulations or an interactive interpreter.
  - `geneticeditor.py`: GUI for editing, running, and visualizing genetic code.
- **Utilities**:
  - `parameters.py`: Defines constants (e.g., codon size, population limits).
  - `checks.py`: Validates genetic code sequences.

## Features

- **Simulation**: Run multiple simulations with customizable population sizes, generations, and execution limits.
- **Interactive Interpreter**: Compile, decompile, and compress genetic code via a REPL.
- **GUI Editor**: Interactively edit, execute, and visualize genetic code with step-by-step execution.
- **Extensive Testing**: Comprehensive unit tests ensure reliability across all modules.
- **Flexible Input/Output**: Support for input files (initial genetic codes) and output files (simulation results).

## Requirements

- Python 3.9 or higher
- PyQt5 (`pip install PyQt5>=5.15.6`)

## Setup

1. **Clone the Repository** (if applicable):
```bash
git clone <repository-url>
cd GeneticAlphabet2.1
```

2. Create a Virtual Environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Running Tests
The project includes a comprehensive test suite using `unittest` to cover all core modules.

```bash
python3 -m unittest discover tests -v
```

Expected output: All tests (across `test_agent.py`, `test_checks.py`, `test_parameters.py`, `test_genetic_strings.py`, `test_interpreter.py`, `test_main.py`, `test_simulation.py`, `test_geneticeditor.py`) should pass.

Alternatively, you can run each module individually, for example:

```bash
python3 -m unittest tests/test_agent.py -v
```

## Usage
### Command-Line Interface (main.py)
The CLI supports two modes: simulation and interactive interpreter.

* Simulation Mode

Run genetic simulations with customizable parameters, including input/output files.

```bash
# Run a simulation with default settings (50 agents, 100 generations, 1 run)
python3 main.py --mode simulation

# Run with custom settings, input file, and output file
python3 main.py --mode simulation --population 10 --generations 20 --max-steps 200 --max-runs 2 --input-file input.txt --output-file results.txt --verbose
```

* Example `input.txt`

```bash
AAAAAA
AAAATC
```

* Example output

```bash
Run 1:
Cumulative Entropy: 1.234
Best Code: AAAAAA

Run 2:
Cumulative Entropy: 1.567
Best Code: AAAATC
```

* Options:
  * `--population`: Number of agents (default: 50, max: parameters.MAX_PROGENY).

  * `--generations`: Generations per run (default: 100, max: parameters.MAX_ITERATIONS).

  * `--max-steps`: Max execution steps per agent (default: parameters.MAX_ITERATIONS).

  * `--max-runs`: Number of simulation runs (default: 1).

  * `--input-file`: Path to file with initial genetic codes.

  * `--output-file`: Path to save simulation results.

  * `--verbose`: Enable detailed output (DYNAMIC_MODE).

* Interpreter Mode
Interactively compile, decompile, or compress genetic code.

```bash
python3 main.py --mode interpreter
```

Example Session:

```bash
Genetic Code Interpreter (type 'quit' to exit)
Commands: compile <code>, decompile <code>, compress <code>
> compile START STOP
Compiled: AAAAUA
> decompile AAAAUA
Decompiled: START STOP
> compress AAAUUUAUA
Compressed: AAAAUA
> quit
```

* Graphical User Interface (`geneticeditor.py`)
Launch the GUI to edit, execute, and visualize genetic code.

```bash
python3 geneticeditor.py
```

- Features:
  - Code Window: Enter high-level code (e.g., “START STOP”).

  - Compiled Window: Enter/view compiled codons (e.g., “AAAAUA”).

  - Table: Displays current code and progeny_code during execution.

- Buttons:
  - Compile: Convert high-level code to codons.

  - Decompile: Convert codons to high-level code.

  - Load: Load compiled code into the agent.

  - Load Progeny: Load progeny_code into the agent.

  - Mutate: Apply random mutations to compiled code.

  - Compress: Remove NO_OP codons from compiled code.

  - Run/Run All: Execute code continuously.

  - Step: Execute one iteration.

  - Stop: Halt continuous execution.

- Controls:
  - Max Iterations: Set execution limit (-1 for unlimited, up to 1000).

  - Wait Interval: Set delay between iterations (default: 1.0 seconds).

- Example Workflow:
  - Enter “START STOP” in the Code Window.

  - Click Compile to get “AAAAUA” in the Compiled Window.

  - Click Load to initialize the agent and populate the table.

  - Click Step to execute one iteration or Run for continuous execution.

  - Click Load Progeny to view progeny_code results.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
