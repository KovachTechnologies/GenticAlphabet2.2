#!/usr/bin/env python3

"""Graphical editor for genetic code using PyQt5."""

import logging
from typing import Optional
from PyQt5 import QtCore, QtGui, QtWidgets
import agent
import genetic_strings
import interpreter

class Ui_MainWindow(QtWidgets.QMainWindow):
    """Main window for the Genetic Editor GUI."""

    def __init__(self):
        """Initialize the main window and instance variables."""
        super().__init__()
        self.agent = agent.Agent(family_id=0)
        self.instruction_pointer: Optional[int] = None
        self.progeny_code: str = ""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.run_step)
        self.setupUi(self)
        logging.info("Initialized Genetic Editor GUI")

    def compress_code(self) -> bool:
        """
        Compress the code in compiledWindow by removing NO_OP codons.

        Returns:
            True if successful, False if code is empty.
        """
        code = self.compiledWindow.toPlainText().strip()
        if not code:
            self.statusbar.showMessage("No code to compress!")
            logging.warning("Attempted to compress empty code")
            return False
        try:
            compressed = interpreter.compress_code(code)
            self.compiledWindow.setText(compressed)
            self.statusbar.showMessage("Code compressed!")
            logging.info("Compressed code: %s", compressed)
            return True
        except ValueError as e:
            self.statusbar.showMessage(f"Compression error: {e}")
            logging.error("Compression error: %s", e)
            return False

    def mutate_code(self) -> bool:
        """
        Mutate the code in compiledWindow.

        Returns:
            True if successful, False if code is empty.
        """
        code = self.compiledWindow.toPlainText().strip()
        if not code:
            self.statusbar.showMessage("No code to mutate!")
            logging.warning("Attempted to mutate empty code")
            return False
        mutated = genetic_strings.mutate(code)
        self.compiledWindow.setText(mutated)
        self.statusbar.showMessage("Code mutated!")
        logging.info("Mutated code: %s", mutated)
        return True

    def load_progeny_code(self) -> bool:
        """
        Load progeny_code into the agent and update tableData.

        Returns:
            True if successful, False if progeny_code is invalid.
        """
        self.instruction_pointer = None
        code = self.progeny_code
        self.progeny_code = ""
        self.tableData.setRowCount(0)

        if not self.agent.init(code):
            self.statusbar.showMessage("Progeny code not executable!")
            logging.error("Failed to load progeny code: %s", code)
            return False

        try:
            tokenized_code = interpreter.tokenize_code(code)
            for row, codon in enumerate(tokenized_code):
                self.tableData.insertRow(row)
                self.tableData.setItem(row, 0, QtWidgets.QTableWidgetItem(codon))
                self.tableData.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
            self.statusbar.showMessage("Progeny code loaded!")
            logging.info("Loaded progeny code: %s", code)
            return True
        except ValueError as e:
            self.statusbar.showMessage(f"Load error: {e}")
            logging.error("Progeny load error: %s", e)
            return False

    def load_data(self) -> bool:
        """
        Load code from compiledWindow into the agent and update tableData.

        Returns:
            True if successful, False if code is invalid.
        """
        self.instruction_pointer = None
        self.progeny_code = ""
        self.tableData.setRowCount(0)
        code = self.compiledWindow.toPlainText().strip()

        if not self.agent.init(code):
            self.statusbar.showMessage("Code not executable!")
            logging.error("Failed to load code: %s", code)
            return False

        try:
            tokenized_code = interpreter.tokenize_code(code)
            for row, codon in enumerate(tokenized_code):
                self.tableData.insertRow(row)
                self.tableData.setItem(row, 0, QtWidgets.QTableWidgetItem(codon))
                self.tableData.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
            self.statusbar.showMessage("Code loaded!")
            logging.info("Loaded code: %s", code)
            return True
        except ValueError as e:
            self.statusbar.showMessage(f"Load error: {e}")
            logging.error("Load error: %s", e)
            return False

    def compile_code(self) -> bool:
        """
        Compile high-level code from codeWindow to codons in compiledWindow.

        Returns:
            True if successful, False if code is empty or invalid.
        """
        code = self.codeWindow.toPlainText().strip()
        if not code:
            self.statusbar.showMessage("No code to compile!")
            logging.warning("Attempted to compile empty code")
            return False
        try:
            compiled = interpreter.compile_code(code)
            self.compiledWindow.setText(compiled)
            self.statusbar.showMessage("Code compiled!")
            logging.info("Compiled code: %s", compiled)
            return True
        except ValueError as e:
            self.statusbar.showMessage(f"Compilation error: {e}")
            logging.error("Compilation error: %s", e)
            return False

    def decompile_code(self) -> bool:
        """
        Decompile code from compiledWindow to high-level code in codeWindow.

        Returns:
            True if successful, False if code is empty.
        """
        code = self.compiledWindow.toPlainText().strip()
        if not code:
            self.statusbar.showMessage("No code to decompile!")
            logging.warning("Attempted to decompile empty code")
            return False
        try:
            decompiled = interpreter.decompile_code(code)
            self.codeWindow.setText(decompiled)
            self.statusbar.showMessage("Code decompiled!")
            logging.info("Decompiled code: %s", decompiled)
            return True
        except ValueError as e:
            self.statusbar.showMessage(f"Decompilation error: {e}")
            logging.error("Decompilation error: %s", e)
            return False

    def run_step(self) -> bool:
        """
        Execute one iteration of the agent's code and update the UI.

        Returns:
            True if execution is complete or an error occurs, False otherwise.
        """
        if self.instruction_pointer is not None and 0 <= self.instruction_pointer - 1 < self.tableData.rowCount():
            self.tableData.item(self.instruction_pointer - 1, 0).setBackground(QtGui.QColor(255, 255, 255))

        if self.agent.iteration():
            self.statusbar.showMessage("Code complete!")
            logging.info("Agent execution completed")
            self.timer.stop()
            return True

        self.instruction_pointer = self.agent.get_instruction_pointer()
        if self.instruction_pointer is None or self.instruction_pointer <= 0:
            self.statusbar.showMessage("Error with instruction pointer!")
            logging.error("Invalid instruction pointer: %s", self.instruction_pointer)
            self.timer.stop()
            return True

        if self.instruction_pointer - 1 < self.tableData.rowCount():
            self.tableData.item(self.instruction_pointer - 1, 0).setBackground(QtGui.QColor(255, 0, 0))
        else:
            self.statusbar.showMessage("Instruction pointer out of bounds!")
            logging.error("Instruction pointer out of bounds: %d", self.instruction_pointer)
            self.timer.stop()
            return True

        if self.agent.progeny_code != self.progeny_code:
            self.progeny_code = self.agent.progeny_code
            try:
                tokenized_code = interpreter.tokenize_code(self.progeny_code) if self.progeny_code else []
                for row in range(max(len(tokenized_code), self.tableData.rowCount())):
                    if row >= self.tableData.rowCount():
                        self.tableData.insertRow(row)
                        self.tableData.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
                    if row < len(tokenized_code):
                        self.tableData.setItem(row, 1, QtWidgets.QTableWidgetItem(tokenized_code[row]))
                    else:
                        self.tableData.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
                logging.debug("Updated progeny code: %s", self.progeny_code)
            except ValueError as e:
                self.statusbar.showMessage(f"Progeny update error: {e}")
                logging.error("Progeny update error: %s", e)
                self.timer.stop()
                return True

        return False

    def run_continuous(self) -> None:
        """Start continuous execution with a timer."""
        max_iterations = self.maxIterations.value()
        interval_ms = int(self.waitInterval.value() * 1000)  # Convert seconds to milliseconds
        self.agent.maximum_iterations = max_iterations if max_iterations >= 0 else float('inf')
        self.timer.start(interval_ms)
        logging.info("Started continuous execution (max_iterations=%s, interval=%dms)", 
                     max_iterations, interval_ms)

    def stop_execution(self) -> None:
        """Stop continuous execution."""
        self.timer.stop()
        self.statusbar.showMessage("Execution stopped!")
        logging.info("Stopped continuous execution")

    def setupUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Set up the UI components and connect signals."""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(933, 724)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableData = QtWidgets.QTableWidget(self.centralwidget)
        self.tableData.setRowCount(20)
        self.tableData.setColumnCount(2)
        self.tableData.setObjectName("tableData")
        item = QtWidgets.QTableWidgetItem()
        self.tableData.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableData.setHorizontalHeaderItem(1, item)
        self.tableData.horizontalHeader().setVisible(True)
        self.tableData.verticalHeader().setCascadingSectionResizes(False)
        self.horizontalLayout.addWidget(self.tableData)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.codeWindow = QtWidgets.QTextEdit(self.centralwidget)
        self.codeWindow.setObjectName("codeWindow")
        self.compiledWindow = QtWidgets.QTextEdit(self.centralwidget)
        self.compiledWindow.setObjectName("compiledWindow")
        self.verticalLayout.addWidget(self.codeWindow)
        self.verticalLayout.addWidget(self.compiledWindow)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalButtonsData = QtWidgets.QHBoxLayout()
        self.horizontalButtonsData.setObjectName("horizontalButtonsData")
        self.runAll = QtWidgets.QPushButton(self.centralwidget)
        self.runAll.setObjectName("runAll")
        self.horizontalButtonsData.addWidget(self.runAll)
        self.run = QtWidgets.QPushButton(self.centralwidget)
        self.run.setEnabled(True)
        self.run.setObjectName("run")
        self.horizontalButtonsData.addWidget(self.run)
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setObjectName("stop")
        self.horizontalButtonsData.addWidget(self.stop)
        self.maxIterations = QtWidgets.QSpinBox(self.centralwidget)
        self.maxIterations.setMinimum(-1)
        self.maxIterations.setMaximum(1000)
        self.maxIterations.setProperty("value", -1)
        self.maxIterations.setObjectName("maxIterations")
        self.horizontalButtonsData.addWidget(self.maxIterations)
        self.step = QtWidgets.QPushButton(self.centralwidget)
        self.step.setObjectName("step")
        self.horizontalButtonsData.addWidget(self.step)
        self.waitInterval = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.waitInterval.setDecimals(1)
        self.waitInterval.setSingleStep(0.1)
        self.waitInterval.setProperty("value", 1.0)
        self.waitInterval.setObjectName("waitInterval")
        self.horizontalButtonsData.addWidget(self.waitInterval)
        self.compile = QtWidgets.QPushButton(self.centralwidget)
        self.compile.setObjectName("compile")
        self.horizontalButtonsData.addWidget(self.compile)
        self.decompile = QtWidgets.QPushButton(self.centralwidget)
        self.decompile.setObjectName("decompile")
        self.horizontalButtonsData.addWidget(self.decompile)
        self.load = QtWidgets.QPushButton(self.centralwidget)
        self.load.setObjectName("load")
        self.horizontalButtonsData.addWidget(self.load)
        self.loadProgeny = QtWidgets.QPushButton(self.centralwidget)
        self.loadProgeny.setObjectName("loadProgeny")
        self.horizontalButtonsData.addWidget(self.loadProgeny)
        self.mutate = QtWidgets.QPushButton(self.centralwidget)
        self.mutate.setObjectName("mutate")
        self.horizontalButtonsData.addWidget(self.mutate)
        self.compress = QtWidgets.QPushButton(self.centralwidget)
        self.compress.setObjectName("compress")
        self.horizontalButtonsData.addWidget(self.compress)
        self.gridLayout.addLayout(self.horizontalButtonsData, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Connect signals
        self.compile.clicked.connect(self.compile_code)
        self.decompile.clicked.connect(self.decompile_code)
        self.load.clicked.connect(self.load_data)
        self.loadProgeny.clicked.connect(self.load_progeny_code)
        self.mutate.clicked.connect(self.mutate_code)
        self.compress.clicked.connect(self.compress_code)
        self.run.clicked.connect(self.run_continuous)
        self.runAll.clicked.connect(self.run_continuous)
        self.step.clicked.connect(self.run_step)
        self.stop.clicked.connect(self.stop_execution)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Translate UI elements."""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Genetic Editor"))
        self.tableData.horizontalHeaderItem(0).setText(_translate("MainWindow", "Code"))
        self.tableData.horizontalHeaderItem(1).setText(_translate("MainWindow", "Progeny"))
        self.codeWindow.setPlaceholderText(_translate("MainWindow", "Enter high-level code here (e.g., START STOP)"))
        self.compiledWindow.setPlaceholderText(_translate("MainWindow", "Enter compiled code here (e.g., AAAAUA)"))
        self.runAll.setText(_translate("MainWindow", "Run All"))
        self.run.setText(_translate("MainWindow", "Run"))
        self.stop.setText(_translate("MainWindow", "Stop"))
        self.step.setText(_translate("MainWindow", "Step"))
        self.compile.setText(_translate("MainWindow", "Compile"))
        self.decompile.setText(_translate("MainWindow", "Decompile"))
        self.load.setText(_translate("MainWindow", "Load"))
        self.loadProgeny.setText(_translate("MainWindow", "Load Progeny"))
        self.mutate.setText(_translate("MainWindow", "Mutate"))
        self.compress.setText(_translate("MainWindow", "Compress"))

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
