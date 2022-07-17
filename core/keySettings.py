# This File contains all classes and functions related 
# to the settings dialog of single keys
# Author 9qUmV4

from os import PathLike
from pathlib import Path
from PySide6.QtWidgets import QDialog, QWidget, QFileDialog, QHBoxLayout
from PySide6.QtCore import Slot, Signal, QUrl
from PySide6.QtGui import QKeyEvent, QMouseEvent
import logging
from core.waveView import WaveChart, WaveView
from PySide6.QtMultimedia import QAudioDecoder

from ui.uic.ui_keySettingsDialog import Ui_Dialog



log = logging.getLogger(__name__)


class KeySettingsDialog(QDialog):
    # Propterties
    _file_path = Path('')

    # Signals
    _update_path = Signal(str)
    dialog_accepted = Signal(str, dict)


    def __init__(
            self, 
            parent: QWidget, 
            key: str,
            lastDir: Path,
            *,
            path: Path,
            label: str,
            startTime: int,
            stopTime: int,
        ) -> None:
        
        super().__init__(parent)

        # self._decoder = QAudioDecoder(self)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # layout = QHBoxLayout(self.ui.waveViewHolder)
        # self.ui.waveView = WaveView()
        # layout.addWidget(self.ui.waveView)

        # Title
        self.setWindowTitle(f"Settings for key {key.upper()}")

        # UI configuration
        self.ui.startTimeDoubleSpinBox.setDecimals(3)
        self.ui.startTimeDoubleSpinBox.setRange(0.0, 86400.0) # Set max to 24 h
        self.ui.startTimeDoubleSpinBox.setSingleStep(1.0)
        self.ui.startTimeDoubleSpinBox.setSuffix(" s")

        self.ui.stopTimeDoubleSpinBox.setDecimals(3)
        self.ui.stopTimeDoubleSpinBox.setRange(0.0, 86400.0) # Set max to 24 h
        self.ui.stopTimeDoubleSpinBox.setSingleStep(1.0)
        self.ui.stopTimeDoubleSpinBox.setSuffix(" s")
        self.ui.stopTimeDoubleSpinBox.setSpecialValueText("END")

        self._update_path.connect(self.ui.pathDisplay.setText)

        self.lastDir = lastDir

        self.key = key
        self.path = path
        self.label = label
        self.startTime = startTime
        self.stopTime = stopTime
        
        self.ui.selectFileButton.clicked.connect(self.selectFile)
        self.accepted.connect(self.dialogAccepted)
    #     self._decoder.bufferReady.connect(self.readBuffer())


    # def readBuffer(self):
    #     buf = self._decoder.read()
    #     print("Format: \t", buf.format())
    #     print("Lenght: \t", buf.duration() * (10**-6), "s")
    #     print("data: \t", type(buf.data()))
    #     print("constData: \t", type(buf.constData()))

    
    def selectFile(self):
        if not self.path == Path():
            openDir = self.path.parent
        else:
            openDir = self.lastDir

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select file to play",
            dir=str(openDir),
            filter="Audio Files (*.mp3 *.wav);;Any (*)",
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
            self.key,
            {
                "path": self.path,
                "label": self.label,
                "startTime": self.startTime,
                "stopTime": self.stopTime,
            }
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
        # self._decoder.setSource(QUrl.fromLocalFile(str(self.path)))
        # self._decoder.start()
        self._update_path.emit(str(self._file_path))


    @property
    def label(self) -> str:
        return self.ui.labelLineEdit.text()

    @label.setter
    def label(self, new: str):
        self.ui.labelLineEdit.setText(new)


    @property
    def startTime(self) -> int:
        return int(self.ui.startTimeDoubleSpinBox.value() * 1000)

    @startTime.setter
    def startTime(self, new: int):
        self.ui.startTimeDoubleSpinBox.setValue(new / 1000)
    

    @property
    def stopTime(self) -> int:
        return int(self.ui.stopTimeDoubleSpinBox.value() * 1000)

    @stopTime.setter
    def stopTime(self, new: int):
        self.ui.stopTimeDoubleSpinBox.setValue(new / 1000)
