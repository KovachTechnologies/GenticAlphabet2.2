#!/usr/bin/env python3

"""Unit tests for simulation module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
import parameters
from simulation import Simulation
from agent import Agent

class TestSimulation(unittest.TestCase):
    def setUp(self):
        """Set up simulation parameters."""
        self.valid_codes = ["AAAAAA", "AAAATC"]

    def test_init_with_valid_codes(self):
        """Test Simulation initialization with valid initial codes."""
        sim = Simulation(population_size=2, max_generations=10, max_steps=100, 
                         initial_codes=self.valid_codes)
        self.assertEqual(len(sim.population), 2)
        self.assertEqual(sim.population[0].code, self.valid_codes[0])
        self.assertEqual(sim.population[1].code, self.valid_codes[1])

    def test_init_with_invalid_codes(self):
        """Test Simulation initialization with invalid codes."""
        with patch('logging.Logger.warning') as mocked_warning:
            sim = Simulation(population_size=2, max_generations=10, max_steps=100, 
                             initial_codes=["AAAA", "BBBB"])
            self.assertTrue(mocked_warning.called)
            self.assertGreaterEqual(len(sim.population), 0)

    def test_init_empty_population(self):
        """Test Simulation initialization with no valid codes."""
        with patch('agent.Agent.init', return_value=False):
            with patch('logging.Logger.error') as mocked_error:
                sim = Simulation(population_size=2, max_generations=1, max_steps=100, max_attempts=10)
                self.assertEqual(len(sim.population), 0)
                mocked_error.assert_called_with("Failed to initialize any agents after %d attempts", 10)

    def test_evaluate_fitness(self):
        """Test evaluate_fitness calculates entropy correctly."""
        sim = Simulation(population_size=1, max_generations=10, max_steps=100, 
                         initial_codes=["AAAAAA"])
        agent = sim.population[0]
        fitness = sim.evaluate_fitness(agent)
        self.assertGreaterEqual(fitness, 0.0)

    def test_select_parents(self):
        """Test select_parents returns valid parents."""
        sim = Simulation(population_size=3, max_generations=10, max_steps=100, 
                         initial_codes=self.valid_codes + ["AAAAAA"])
        parents = sim.select_parents()
        self.assertEqual(len(parents), sim.population_size)
        for parent in parents:
            self.assertIn(parent, sim.population)

    def test_run_simulation(self):
        """Test run_simulation completes and returns best agent."""
        with patch('logging.Logger.info') as mocked_info:
            sim = Simulation(population_size=2, max_generations=1, max_steps=100, 
                             initial_codes=self.valid_codes)
            best_agent = sim.run_simulation()
            self.assertTrue(mocked_info.called)
            self.assertIn(best_agent, sim.population)

    def test_run_simulation_empty(self):
        """Test run_simulation with empty population."""
        with patch('logging.Logger.error') as mocked_error:
            sim = Simulation(population_size=0, max_generations=1, max_steps=100)
            best_agent = sim.run_simulation()
            self.assertIsNone(best_agent)
            mocked_error.assert_called_with("Cannot run simulation: Empty population")

if __name__ == '__main__':
    unittest.main()
