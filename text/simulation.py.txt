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
                 initial_codes: Optional[List[str]] = None, max_attempts: int = 100):
        """
        Initialize the simulation with a population of agents.

        Args:
            population_size: Number of agents in the population.
            max_generations: Maximum number of generations to run.
            max_steps: Maximum execution steps per agent.
            initial_codes: Optional list of initial genetic codes.
            max_attempts: Maximum attempts to initialize random agents (default: 100).
        """
        self.population_size = min(population_size, parameters.MAX_PROGENY)
        self.max_generations = min(max_generations, parameters.MAX_ITERATIONS)
        self.max_steps = min(max_steps, parameters.MAX_ITERATIONS)
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
        Evaluate the fitness of an agent based on its progeny code entropy.

        Args:
            agent: The agent to evaluate.

        Returns:
            The fitness score (entropy of progeny code or code).
        """
        code = agent.progeny_code or agent.code
        fitness = genetic_strings.entropy(code)
        if parameters.DYNAMIC_MODE:
            logging.debug("Agent (family_id=%d) fitness: %.3f (code: %s)", 
                          agent.family_id, fitness, code)
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

        for gen in range(self.max_generations):
            self.generation = gen + 1
            if parameters.DYNAMIC_MODE:
                logging.debug("Generation %d/%d", self.generation, self.max_generations)

            # Evaluate and select parents
            parents = self.select_parents()
            if not parents:
                logging.warning("No parents selected for generation %d", self.generation)
                break

            # Create new population
            new_population = []
            for i in range(self.population_size):
                parent = random.choice(parents)
                code = genetic_strings.mutate(parent.code)
                agent = Agent(family_id=i)
                if agent.init(code):
                    new_population.append(agent)
                    if parameters.DYNAMIC_MODE:
                        logging.debug("New agent (family_id=%d) code: %s", i, code)
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
                logging.debug("Best fitness in generation %d: %.3f", 
                              self.generation, self.evaluate_fitness(best_agent))

        # Return the best agent
        best_agent = max(self.population, key=self.evaluate_fitness, default=None)
        if best_agent:
            logging.info("Simulation completed. Best agent (family_id=%d) fitness: %.3f", 
                         best_agent.family_id, self.evaluate_fitness(best_agent))
        else:
            logging.warning("No best agent found")
        return best_agent
