#!/usr/bin/env python3

"""Simulation for evolving a population of genetic agents."""

import random
from typing import List, Optional
import logging
import parameters
import genetic_strings
from agent import Agent

class Simulation:
    def __init__(self, population_size: int, max_generations: int, max_steps: int, 
                 initial_codes: Optional[List[str]] = None, max_attempts: int = 100,
                 target_peptide: Optional[str] = None):
        """
        Initialize the simulation with a population of agents.

        Args:
            population_size: Number of agents in the population.
            max_generations: Maximum number of generations to run.
            max_steps: Maximum execution steps per agent.
            initial_codes: Optional list of initial genetic codes.
            max_attempts: Maximum attempts to initialize random agents (default: 100).
            target_peptide: Optional target peptide sequence to search for.
        """
        self.population_size = min(population_size, parameters.MAX_PROGENY)
        self.max_generations = min(max_generations, parameters.MAX_ITERATIONS)
        self.max_steps = min(max_steps, parameters.MAX_ITERATIONS)
        self.target_peptide = target_peptide
        self.generation = 0
        self.population: List[Agent] = []

        if initial_codes:
            for i, code in enumerate(initial_codes[:self.population_size]):
                agent = Agent(family_id=i)
                if agent.init(code):
                    self.population.append(agent)
                else:
                    logging.warning("Failed to initialize agent with code: %s", code)

        # Try to fill remaining population with random codes
        attempts = 0
        while len(self.population) < self.population_size and attempts < max_attempts:
            code = genetic_strings.create_string()
            agent = Agent(family_id=len(self.population))
            if agent.init(code):
                self.population.append(agent)
            else:
                logging.warning("Failed to initialize agent with random code")
            attempts += 1

        if not self.population:
            logging.error("Failed to initialize any agents after %d attempts", max_attempts)
            self.population = []

    def evaluate_fitness(self, agent: Agent) -> float:
        """
        Evaluate the fitness of an agent based on its progeny code entropy and peptide match.

        Args:
            agent: The agent to evaluate.

        Returns:
            The fitness score.
        """
        fitness = agent.evaluate_fitness(target_peptide=self.target_peptide)
        if parameters.DYNAMIC_MODE:
            logging.debug("Agent (family_id=%d) fitness: %.3f (code: %s, progeny: %s, peptide: %s)", 
                          agent.family_id, fitness, agent.code, agent.progeny_code, 
                          agent.translate_to_peptide())
        return fitness

    def select_parents(self) -> List[Agent]:
        """
        Select parents for the next generation using tournament selection.

        Returns:
            List of selected parent agents.
        """
        tournament_size = min(3, len(self.population))
        parents = []
        for _ in range(self.population_size):
            tournament = random.sample(self.population, tournament_size)
            best = max(tournament, key=self.evaluate_fitness, default=None)
            if best:
                parents.append(best)
        return parents

    def run_simulation(self) -> Optional[Agent]:
        """
        Run the simulation for the specified number of generations.

        Returns:
            The best agent from the final generation, or None if population is empty.
        """
        if not self.population:
            logging.error("Cannot run simulation: Empty population")
            return None

        # Initial iteration for first generation (no mutation)
        for agent in self.population:
            for _ in range(self.max_steps):
                if agent.iteration():
                    break
            logging.debug("Initial agent (family_id=%d) progeny_code: %s, peptide: %s", 
                          agent.family_id, agent.progeny_code, agent.translate_to_peptide())

        for gen in range(self.max_generations):
            self.generation = gen + 1
            if parameters.DYNAMIC_MODE:
                logging.debug("Generation %d/%d", self.generation, self.max_generations)

            # Evaluate and select parents
            parents = self.select_parents()
            if not parents:
                logging.warning("No parents selected for generation %d", self.generation)
                break

            # Create new population with mutations
            new_population = []
            for i in range(self.population_size):
                parent = random.choice(parents)
                # Only mutate in later generations to preserve initial codes
                code = genetic_strings.mutate(parent.code) if gen > 0 else parent.code
                agent = Agent(family_id=i)
                if agent.init(code):
                    # Run iterations for new agent
                    for _ in range(self.max_steps):
                        if agent.iteration():
                            break
                    new_population.append(agent)
                    if parameters.DYNAMIC_MODE:
                        logging.debug("New agent (family_id=%d) code: %s, progeny_code: %s, peptide: %s", 
                                      i, code, agent.progeny_code, agent.translate_to_peptide())
                else:
                    logging.warning("Failed to initialize new agent with code: %s", code)

            self.population = new_population if new_population else self.population

            # Check for convergence or empty population
            if not self.population:
                logging.error("Population extinct at generation %d", self.generation)
                return None

            # Log generation summary
            best_agent = max(self.population, key=self.evaluate_fitness, default=None)
            if best_agent and parameters.DYNAMIC_MODE:
                logging.debug("Best fitness in generation %d: %.3f (progeny_code: %s, peptide: %s)", 
                              self.generation, self.evaluate_fitness(best_agent), 
                              best_agent.progeny_code, best_agent.translate_to_peptide())

        # Return the best agent
        best_agent = max(self.population, key=self.evaluate_fitness, default=None)
        if best_agent:
            logging.info("Simulation completed. Best agent (family_id=%d) fitness: %.3f, progeny_code: %s, peptide: %s", 
                         best_agent.family_id, self.evaluate_fitness(best_agent), 
                         best_agent.progeny_code, best_agent.translate_to_peptide())
        else:
            logging.warning("No best agent found")
        return best_agent
