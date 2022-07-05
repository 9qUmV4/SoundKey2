# This File contains all classes and functions related 
# to the settings dialog of single keys
# Author 9qUmV4

from os import PathLike
from pathlib import Path
from PySide6.QtWidgets import QDialog, QWidget, QFileDialog
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QKeyEvent, QMouseEvent
import logging

from ui.uic.ui_keySettingsDialog import Ui_Dialog



log = logging.getLogger(__name__)


class KeySettingsDialog(QDialog):
    # Propterties
    _file_path = Path('')

    # Signals
    _update_path = Signal(str)
    dialog_accepted = Signal(Path, str)


    def __init__(
            self, 
            parent: QWidget, 
            key: str,
            *,
            path: Path,
            label: str 
        ) -> None:
        
        super().__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle(f"Settings for key {key.upper()}")
        self.setStyleSheet("""
            QPushButton {
                background: rgb(70, 70, 70); 
                color: white;
            }
            QAbstractScrollArea {
                border-width: 0px;
            }
            QLineEdit {
                background: rgb(70, 70, 70)
            }
            
        """)


        self.key = key
        self.path = path
        self.label = label
        
        self.ui.selectFileButton.clicked.connect(self.selectFile)
        self._update_path.connect(self.ui.pathDisplay.setText)
        self.accepted.connect(self.dialogAccepted)

    
    def selectFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select file to play",
            dir=str(self.path.parent),         # TODO Implement saving last directory
            filter="Audio Files (*.mp3);;Any (*)",
        )
        if file_path == "":
            log.info("File dialog 'Select file to play' canceled by user")
            return None
        else:
            file_path = Path(file_path)
            logging.debug(f"File dialog 'Select file to play' closed returning '{file_path}'")
            self.path = file_path


    @Slot()
    def dialogAccepted(self):
        self.dialog_accepted.emit(
            self.path,
            self.label
        )
        


    # Events
    # ------


    # Properties
    # ----------
    @property
    def path(self):
        return self._file_path


    @path.setter
    def path(self, new_path: PathLike):
        new_path = Path(new_path)
        self._file_path = new_path
        self._update_path.emit(str(self._file_path))


    @property
    def label(self) -> str:
        return self.ui.labelEdit.text()

    @label.setter
    def label(self, new: str):
        self.ui.labelEdit.setText(new)
