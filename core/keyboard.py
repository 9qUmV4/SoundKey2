
import logging
from os import PathLike
from pathlib import Path
from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QFrame
from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QMouseEvent, QShortcut, QPalette, QColor

from .keySettings import KeySettingsDialog


log = logging.getLogger(__name__)


KEYBOARD_LAYOUT = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", ],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", ],
    [None, "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"],
]


# ########################################
#               KEYBUTTON
# ########################################
class KeyButton:

    def __init__(
        self, 
        parent: QWidget, 
        key: str,
        ) -> None:
        
        # UI
        self.ui = PushButton(parent)
        
        # Audio Output
        self._audioOutput = QAudioOutput()
        self._audioOutput.setVolume(.5) # TODO

        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audioOutput)
        
        # Argument parsing
        self._key = key.lower()
        self.label = ''
        self.path = Path()

        # Keyboard Shortcut
        self._shortcut = QShortcut(self.key, parent)

        # Connectors
        self.ui.clicked.connect(self.togglePlay)
        self._shortcut.activated.connect(self.togglePlay)
        self.ui.left_duble_click.connect(self._openSettingsDialog)
        self._player.playbackStateChanged.connect(self.ui._updateButtonColor)

        self._can_play = False



    #  PROPERTIES
    # ------------
    # key
    @property
    def key(self) -> str:
        return self._key

    # label
    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, new: str):
        log.debug(f"Setting label of key '{self.key} to '{new}'")
        self._label = new
        self.ui.setText(f"{self.key.upper()}\n{new}")

    # path
    @property
    def path(self) -> Path:
        return self._path
    
    @path.setter
    def path(self, new: PathLike | str):
        new = Path(new)
        log.debug(f"Setting path of key '{self.key} to '{new}'")
        self._path = new
        if new.is_file():
            self._can_play = True
            self._player.setSource(QUrl.fromLocalFile(str(new)))
        else:
            self._can_play = False
            self._player.setSource(QUrl())

    # _can_play
    @property
    def _can_play(self) -> bool:
        return self.__can_play
    
    @_can_play.setter
    def _can_play(self, new: bool):
        self.__can_play = new
        self.ui.setCheckable(new)
        if new: # If button is active
            self.ui.setStyleSheet("""
            QPushButton {
                background: rgb(70, 70, 70); 
                color: white;
                border-color: rgb(0, 189, 13);
            } 
            QPushButton::checked {
                background: rgb(0, 189, 13); 
                color: white;
                border-color: rgb(0, 189, 13);
            }
            """)
        else: # If button is inactive
            self.ui.setStyleSheet("""
            QPushButton {
                background:rgb(51, 51, 51); 
                color: rgb(127, 127, 127);
            } 
            QPushButton::checked {
                background:rgb(51, 51, 51);
                color: rgb(127, 127, 127);
            }
            """)


    # is_plaing
    @property
    def is_plaing(self) -> bool:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            return True
        else:
            False



    #  METHODES
    # ----------
    def play(self) -> bool:
        """Trys to start playing. Returns True and plays when possible, else returns False."""
        if self._can_play:
            if not self.is_plaing:
                log.info(f"Key '{self.key}' starts playing (file: '{self.path}')")
                self._player.play()
                return True
            else:
                log.warning(f"Key '{self.key}' is already playing")
        else:
            log.warning(f"Key '{self.key}' cannot play because no file to play is given")
            return False

    def stop(self):
        """Trys to stop playing. Returns True if suceccfull and False, if not."""
        if self.is_plaing:
            self._player.stop()
            log.info(f"Key '{self.key}' stopped playing")
            return True
        else:
            log.warning(f"Key '{self.key}' cannot stop playing, nothing is playing")
            return False

    def togglePlay(self):
        """Toggles playing."""
        if self.is_plaing:
            self.stop()
        else:
            self.play()


    def updateSettings(
        self,
        *,
        label: str = '',
        path: PathLike | str = Path(),
        **kwargs):
        """
        Updates the object according to given settings. 
        This is a conviniens function for setting attributes.
        """
        self.label = label
        self.path = path

    def getSettings(self):
        """Returns Settings to save."""
        return {
            "path": str(self.path),
            "label": self.label
        }

    def new(self):
        """Sets everything to default values."""
        self.path = Path()
        self.label = ""
        

    def _openSettingsDialog(self):
        """Opens the Settings Dialog."""
        dlg = KeySettingsDialog(
            self.ui, 
            self.key,
            path=self.path,
            label=self.label,
        )

        dlg.dialog_accepted.connect(self._closeSettingsDialog)
        dlg.exec()


    def _closeSettingsDialog(
            self,
            path,
            label,
        ):
        """Handles the new settings, after the SettingsDialog got closed.s"""        
        self.path = path
        self.label = label





# ########################################
#               PUSHBUTTON
# ########################################
class PushButton(QPushButton):
    

    left_duble_click = Signal()



    #  METHODES
    # ----------
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.setFocusPolicy(Qt.NoFocus)


    def _updateButtonColor(self, newState):
        self.setChecked(newState == QMediaPlayer.PlaybackState.PlayingState)
    

    #  EVENTS
    # --------
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.left_duble_click.emit()
        return super().mouseDoubleClickEvent(event)


# ########################################
#               KEYBOARD
# ########################################

class Keyboard(QFrame):
    def __init__(self, parent) -> None:
        super(Keyboard, self).__init__(parent=parent)

        # Generate Keyboard
        layout = QGridLayout(self)
        self._key_list = []

        for row_i, row in enumerate(KEYBOARD_LAYOUT):
            for char_i, char in enumerate(row):
                if char is not None:
                    setattr(self, f'key_{char}', KeyButton(self, char))
                    layout.addWidget(getattr(self, f'key_{char}').ui, row_i, char_i)
                    self._key_list.append(char)

        self.setLayout(layout)


    def getSettings(self):
        return {key: getattr(self, f'key_{key}').getSettings() for key in self._key_list}

    def updateSettings(self, **kwargs):
        """Updates the settings accordingly"""
        for k, v in kwargs.items():
            getattr(self, f'key_{k}').updateSettings(**v)
    
    def new(self):
        """Sets everything to default values."""
        for k in self._key_list:
            getattr(self, f'key_{k}').new()