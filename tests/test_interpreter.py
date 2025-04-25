#!/usr/bin/env python3

"""Unit tests for interpreter module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import parameters
from interpreter import compile_code, tokenize_code, decompile_code, compress_code

class TestInterpreter(unittest.TestCase):
    def test_compile_code_valid(self):
        """Test compile_code with valid operations."""
        high_level = "START STOP"
        expected = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.assertEqual(compile_code(high_level), expected)

    def test_compile_code_with_no_ops(self):
        """Test compile_code with operations and NO_OP codons."""
        high_level = "START UUU CCC STOP"
        expected = parameters.OPERATIONS["START"][0] + "UUU" + "CCC" + parameters.OPERATIONS["STOP"][0]
        self.assertEqual(compile_code(high_level), expected)

    def test_compile_code_empty(self):
        """Test compile_code with empty input."""
        self.assertEqual(compile_code(""), "")

    def test_compile_code_invalid_token(self):
        """Test compile_code with an invalid token."""
        with self.assertRaisesRegex(ValueError, "Invalid token: XYZ"):
            compile_code("START XYZ STOP")

    def test_tokenize_code_valid(self):
        """Test tokenize_code with a valid code string."""
        code = "AAAAAA"  # Two AAA codons
        expected = ["AAA", "AAA"]
        self.assertEqual(tokenize_code(code), expected)

    def test_tokenize_code_empty(self):
        """Test tokenize_code with empty code."""
        self.assertEqual(tokenize_code(""), [])

    def test_tokenize_code_invalid_length(self):
        """Test tokenize_code with invalid code length."""
        with self.assertRaisesRegex(ValueError, "Code length 4 is not a multiple of CODON_SIZE 3"):
            tokenize_code("AAAA")

    def test_decompile_code_operations(self):
        """Test decompile_code with operation codons."""
        code = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        expected = "START STOP"
        self.assertEqual(decompile_code(code), expected)

    def test_decompile_code_no_op(self):
        """Test decompile_code with a NO_OP codon."""
        code = "UUU"
        self.assertEqual(decompile_code(code), "UUU")

    def test_decompile_code_mixed(self):
        """Test decompile_code with operations and NO_OP codons."""
        code = parameters.OPERATIONS["START"][0] + "UUU" + parameters.OPERATIONS["STOP"][0]
        expected = "START UUU STOP"
        self.assertEqual(decompile_code(code), expected)

    def test_decompile_code_empty(self):
        """Test decompile_code with empty code."""
        self.assertEqual(decompile_code(""), "")

    def test_compress_code_operations(self):
        """Test compress_code with only operation codons."""
        code = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.assertEqual(compress_code(code), code)

    def test_compress_code_no_ops(self):
        """Test compress_code with NO_OP codons."""
        code = parameters.OPERATIONS["START"][0] + "UUU" + parameters.OPERATIONS["STOP"][0]
        expected = parameters.OPERATIONS["START"][0] + parameters.OPERATIONS["STOP"][0]
        self.assertEqual(compress_code(code), expected)

    def test_compress_code_empty(self):
        """Test compress_code with empty code."""
        self.assertEqual(compress_code(""), "")

if __name__ == '__main__':
    unittest.main()
