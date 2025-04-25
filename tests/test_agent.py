#!/usr/bin/env python3

"""Unit tests for agent module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import parameters
from agent import Agent

class TestAgent(unittest.TestCase):
    def setUp(self):
        """Set up an Agent instance for testing."""
        self.agent = Agent(family_id=0)

    def test_init_executable(self):
        """Test init with an executable code string."""
        code = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.assertTrue(self.agent.init(code))
        self.assertEqual(self.agent.code, code)
        self.assertEqual(self.agent.tape, [parameters.OPERATIONS["START"][0], parameters.OPERATIONS["STOP"][0]])
        self.assertEqual(self.agent.program_counter, 0)
        self.assertEqual(self.agent.progeny_code, "")

    def test_init_non_executable(self):
        """Test init with a non-executable code string."""
        code = "INVALID"
        self.assertFalse(self.agent.init(code))
        self.assertEqual(self.agent.code, "")
        self.assertEqual(self.agent.tape, [])
        self.assertEqual(self.agent.program_counter, 0)
        self.assertEqual(self.agent.progeny_code, "")

    def test_is_executable(self):
        """Test is_executable method via init."""
        code = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.assertTrue(self.agent.set_code(code))
        self.assertEqual(self.agent.code, code)
        self.assertEqual(self.agent.tape, [parameters.OPERATIONS["START"][0], parameters.OPERATIONS["STOP"][0]])

    def test_iteration_stop(self):
        """Test iteration with a STOP instruction."""
        code = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.agent.set_code(code)
        self.assertFalse(self.agent.iteration())  # START
        self.assertEqual(self.agent.program_counter, 1)
        self.assertTrue(self.agent.iteration())   # STOP
        self.assertEqual(self.agent.program_counter, 1)
        self.assertEqual(self.agent.progeny_code, parameters.OPERATIONS["START"][0])

    def test_iteration_copy(self):
        """Test iteration with a COPY instruction."""
        code = parameters.OPERATIONS["COPY"][0] + parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.agent.set_code(code)
        self.assertFalse(self.agent.iteration())  # COPY
        self.assertEqual(self.agent.program_counter, 2)  # Skips START
        self.assertEqual(self.agent.progeny_code, parameters.OPERATIONS["START"][0])
        self.assertTrue(self.agent.iteration())   # STOP
        self.assertEqual(self.agent.progeny_code, parameters.OPERATIONS["START"][0])

    def test_iteration_jump(self):
        """Test iteration with a JUMP instruction."""
        code = (parameters.OPERATIONS["JUMP"][0] + parameters.OPERATIONS["STOP"][0] + 
                parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0])
        self.agent.set_code(code)
        self.assertFalse(self.agent.iteration())  # JUMP
        self.assertEqual(self.agent.program_counter, 2)  # Jumped to START
        self.assertFalse(self.agent.iteration())  # START
        self.assertEqual(self.agent.program_counter, 3)
        self.assertEqual(self.agent.progeny_code, parameters.OPERATIONS["START"][0])

    def test_iteration_cond_if(self):
        """Test iteration with COND and IF instructions."""
        code = (parameters.OPERATIONS["COND"][0] + parameters.OPERATIONS["IF"][0] + 
                parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0])
        self.agent.set_code(code)
        self.assertFalse(self.agent.iteration())  # COND
        self.assertEqual(self.agent.program_counter, 1)
        self.assertFalse(self.agent.iteration())  # IF
        self.assertEqual(self.agent.program_counter, 3)  # Skips START
        self.assertEqual(self.agent.progeny_code, parameters.OPERATIONS["START"][0])
        self.assertTrue(self.agent.iteration())   # STOP

    def test_run_full_execution(self):
        """Test run method with a full program."""
        code = (parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["COPY"][0] + 
                parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0])
        self.agent.set_code(code)
        while not self.agent.iteration():
            print(f"DEBUG: progeny_code={self.agent.progeny_code}, program_counter={self.agent.program_counter}")
        print(f"DEBUG: Final progeny_code={self.agent.progeny_code}, program_counter={self.agent.program_counter}")
        self.assertEqual(self.agent.progeny_code, parameters.OPERATIONS["START"][0] * 2)
        self.assertEqual(self.agent.program_counter, 3)
        self.assertEqual(self.agent.code, code)
