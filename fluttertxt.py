from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from dataclasses import dataclass
from functools import partial
import sys
import os
import json

# requirements:
#   pip install PyQt6

# TODO:
#   clean/refactor
#   manually handle hotkeys
#   auto expand toolbar (custom widget?)
#   file menu
#   prefix input
#   tab input
#   hidden shortcuts
#   floating toolbar mode? (external output)
#   apl mappings
#   button color
#   persistent settings?
#   test on windows
#   shell commands
#   status bar (persistent, selection info, line/col)
#   font/font size selection
#   per-mapping font

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

@dataclass
class SymbolInfo:
    symbol:   str
    tooltip:  str
    shortcut: str
    output:   str

class MainWindow(QMainWindow):
    def __init__(self):
        self.mappings = []
        self.mappingnames = []
        self.get_mappings()

        super().__init__()
        self.setWindowTitle("Hello!!")
        self.setGeometry(123, 123, 666, 420)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.editor = QPlainTextEdit()
        font = QFont("JuliaMono")
        font.setPointSize(12)
        self.editor.setFont(font)
        self.editor.textChanged.connect(self.text_changed)
        self.setCentralWidget(self.editor)

        toolbar2 = QToolBar()
        toolbar2.setMovable(False)
        toolbar2.setFloatable(False)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar2.addWidget(spacer)
        combo = QComboBox()
        toolbar2.addWidget(combo)
        combo.insertItems(0, self.mappingnames)
        combo.currentIndexChanged.connect(self.index_changed)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar2)

        self.addToolBarBreak(Qt.ToolBarArea.TopToolBarArea)

        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("""
            QToolButton{
                padding: 0px;
                font-family: 'JuliaMono';
                font-size: 18px;
                margin: 0px;
                max-width: 16px;
            }
            QToolBar{
                padding: 1px;
                min-width: 20px;
            }""");
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.get_actions()
        self.index_changed(0)
        self.text_changed()

    def insert_symbol(self, character):
        self.editor.insertPlainText(character)
        self.editor.ensureCursorVisible()

    def text_changed(self):
        charlen = str(len(self.editor.toPlainText()))
        bytelen = str(len(self.editor.toPlainText().encode('utf-8')))
        self.status.showMessage("chars: " + charlen + ", bytes: " + bytelen)

    def index_changed(self, index):
        self.toolbar.clear()
        for action in self.actions[index]:
            self.toolbar.addAction(action)

    def get_mappings(self):
        jsonpath = os.path.join(CURRENT_DIR, "config.json")
        with open(jsonpath, encoding="utf-8") as f:
            read_data = f.read()
        j = json.loads(read_data)
        globalmodifier = j["modifier"] if "modifier" in j else None
        for name, mapping in j["mappings"].items():
            self.mappingnames.append(name)
            symbols = []
            for symbol, info in mapping.items():
                tooltip = info["tooltip"] if "tooltip" in info else None
                key = info["key"] if "key" in info else None
                shortcut = None
                if key is not None:
                    modifier = info["modifier"] if "modifier" in info else globalmodifier
                    if modifier is None:
                        shortcut = key
                    else:
                        if len(key) == 1 and key.isalpha() and key.isupper():
                            modifier += "+Shift"
                        shortcut = modifier + "+" + key
                output = info["output"] if "output" in info else symbol
                symbols.append(SymbolInfo(symbol, tooltip, shortcut, output))
            self.mappings.append(symbols)

    def get_actions(self):
        self.actions = []
        for mappinglist in self.mappings:
            actionlist = []
            for info in mappinglist:
                symbol = info.symbol
                shortcut = info.shortcut
                tooltip = symbol
                if shortcut is not None: tooltip += " [" + shortcut + "]"
                if info.tooltip is not None: tooltip += "\n" + info.tooltip
                output = info.output
                
                action = QAction(symbol, self)
                action.setToolTip(tooltip)
                if shortcut is not None: action.setShortcut(shortcut)
                action.triggered.connect(partial(self.insert_symbol, output))
                actionlist.append(action)
            self.actions.append(actionlist)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_path = os.path.join(CURRENT_DIR, "font", "JuliaMono", "JuliaMono-Regular.ttf")
    _id = QFontDatabase.addApplicationFont(font_path)
    if QFontDatabase.applicationFontFamilies(_id) == -1:
        print("error loading font")
    app.setApplicationName("pytext01")
    window = MainWindow()
    window.show()
    app.exec()
