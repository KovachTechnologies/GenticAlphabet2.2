#!/usr/bin/env python3

"""Unit tests for geneticeditor module."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QTableWidget, QStatusBar
import parameters
from geneticeditor import Ui_MainWindow

class TestGeneticEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize QApplication for all tests."""
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication."""
        cls.app.quit()
        del cls.app

    def setUp(self):
        """Set up a mock Ui_MainWindow instance."""
        self.ui = Ui_MainWindow()
        # Mock GUI components to avoid widget creation
        self.ui.main_window = MagicMock(spec=QMainWindow)
        self.ui.tableData = MagicMock(spec=QTableWidget)
        self.ui.statusbar = MagicMock(spec=QStatusBar)
        self.ui.codeWindow = MagicMock(spec=QTextEdit)
        self.ui.compiledWindow = MagicMock(spec=QTextEdit)
        # Mock agent to isolate dependencies
        self.ui.agent = MagicMock()
        # Avoid calling setupUi to prevent real widget creation
        self.ui.setupUi = MagicMock()

    def test_compile_code_valid(self):
        """Test compile_code with valid high-level code."""
        self.ui.codeWindow.toPlainText.return_value = "START STOP"
        self.ui.compiledWindow.setText = MagicMock()
        self.ui.statusbar.showMessage = MagicMock()
        result = self.ui.compile_code()
        self.assertTrue(result)
        self.ui.compiledWindow.setText.assert_called_with("AAAAUA")
        self.ui.statusbar.showMessage.assert_called_with("Code compiled!")

    def test_compile_code_empty(self):
        """Test compile_code with empty code."""
        self.ui.codeWindow.toPlainText.return_value = ""
        self.ui.statusbar.showMessage = MagicMock()
        result = self.ui.compile_code()
        self.assertFalse(result)
        self.ui.statusbar.showMessage.assert_called_with("No code to compile!")

    def test_decompile_code_valid(self):
        """Test decompile_code with valid codon sequence."""
        self.ui.compiledWindow.toPlainText.return_value = "AAAAUA"
        self.ui.codeWindow.setText = MagicMock()
        self.ui.statusbar.showMessage = MagicMock()
        result = self.ui.decompile_code()
        self.assertTrue(result)
        self.ui.codeWindow.setText.assert_called_with("START STOP")
        self.ui.statusbar.showMessage.assert_called_with("Code decompiled!")

    def test_decompile_code_empty(self):
        """Test decompile_code with empty code."""
        self.ui.compiledWindow.toPlainText.return_value = ""
        self.ui.statusbar.showMessage = MagicMock()
        result = self.ui.decompile_code()
        self.assertFalse(result)
        self.ui.statusbar.showMessage.assert_called_with("No code to decompile!")

    def test_mutate_code_valid(self):
        """Test mutate_code with valid code."""
        self.ui.compiledWindow.toPlainText.return_value = "AAAAAA"
        self.ui.compiledWindow.setText = MagicMock()
        self.ui.statusbar.showMessage = MagicMock()
        with patch("genetic_strings.mutate", return_value="AAAATC"):
            result = self.ui.mutate_code()
        self.assertTrue(result)
        self.ui.compiledWindow.setText.assert_called_with("AAAATC")
        self.ui.statusbar.showMessage.assert_called_with("Code mutated!")

    def test_mutate_code_empty(self):
        """Test mutate_code with empty code."""
        self.ui.compiledWindow.toPlainText.return_value = ""
        self.ui.statusbar.showMessage = MagicMock()
        result = self.ui.mutate_code()
        self.assertFalse(result)
        self.ui.statusbar.showMessage.assert_called_with("No code to mutate!")

    def test_load_data_valid(self):
        """Test load_data with valid code."""
        self.ui.compiledWindow.toPlainText.return_value = "AAAAAA"
        self.ui.agent.init.return_value = True
        with patch("interpreter.tokenize_code", return_value=["AAA", "AAA"]):
            result = self.ui.load_data()
        self.assertTrue(result)
        self.ui.statusbar.showMessage.assert_called_with("Code loaded!")
        self.ui.tableData.insertRow.assert_any_call(0)
        self.ui.tableData.insertRow.assert_any_call(1)

    def test_load_data_invalid(self):
        """Test load_data with invalid code."""
        self.ui.compiledWindow.toPlainText.return_value = "AAAA"
        self.ui.agent.init.return_value = False
        result = self.ui.load_data()
        self.assertFalse(result)
        self.ui.statusbar.showMessage.assert_called_with("Code not executable!")

    def test_load_progeny_code_valid(self):
        """Test load_progeny_code with valid progeny code."""
        self.ui.progeny_code = "AAAAAA"
        self.ui.agent.init.return_value = True
        with patch("interpreter.tokenize_code", return_value=["AAA", "AAA"]):
            result = self.ui.load_progeny_code()
        self.assertTrue(result)
        self.ui.statusbar.showMessage.assert_called_with("Progeny code loaded!")
        self.ui.tableData.insertRow.assert_any_call(0)
        self.ui.tableData.insertRow.assert_any_call(1)

    def test_load_progeny_code_invalid(self):
        """Test load_progeny_code with invalid progeny code."""
        self.ui.progeny_code = "AAAA"
        self.ui.agent.init.return_value = False
        result = self.ui.load_progeny_code()
        self.assertFalse(result)
        self.ui.statusbar.showMessage.assert_called_with("Progeny code not executable!")

if __name__ == "__main__":
    unittest.main()
