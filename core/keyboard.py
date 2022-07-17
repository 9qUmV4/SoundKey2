
import logging
from os import PathLike
from pathlib import Path
from typing import overload
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

    END_OF_FILE_TIME = 0.0

    DEFAULT_LABEL = ""
    DEFAULT_PATH = Path()
    DEFAULT_START_TIME = 0
    DEFAULT_STOP_TIME = 0
    



    def __init__(
        self, 
        parent: QWidget, 
        key: str,
        ) -> None:
        
        # UI
        self.ui = PushButton(parent)
        self.ui.setProperty("keyboardButton", True)
        
        # Audio Output
        self._audioOutput = QAudioOutput()
        self._audioOutput.setVolume(1.0) # TODO

        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audioOutput)
        
        # Argument parsing
        self._key = key.lower()
        
        # Set attributes
        self.new()
        self._can_play = False

        # Keyboard Shortcut
        self._shortcut = QShortcut(self.key, parent)

        # Connectors UI
        self._player.playbackStateChanged.connect(self.ui._updateButtonColor)

        # Connectors function
        self.ui.clicked.connect(self.togglePlay)
        self._shortcut.activated.connect(self.togglePlay)
        self.ui.left_duble_click.connect(self._openSettingsDialog)
        self._player.positionChanged.connect(self._auto_stop)




    #  PROPERTIES
    # ------------
    # key
    @property
    def key(self) -> str:
        """
        The letter of the key stored as string. 
        This attribute is read only, because the key must be set when initalizing.
        """
        return self._key

    # label
    @property
    def label(self) -> str:
        """The label of the key. Stored as string. Defaults to ''."""
        return self._label

    @label.setter
    def label(self, new: str):
        log.debug(f"Setting label of key '{self.key}' to '{new}'")
        self._label = new
        self.ui.setText(f"{self.key.upper()}\n{new}")

    # path
    @property
    def path(self) -> Path:
        """
        The path to the media file. 
        Accepts any PathLike or string and returns a pathlib.Path. Defaults to Path().
        """
        return self._path
    
    @path.setter
    def path(self, new: PathLike | str):
        new = Path(new)
        log.debug(f"Setting path of key '{self.key}' to '{new}'")
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
        """Check, if the file is playable."""
        return self.__can_play
    
    @_can_play.setter
    def _can_play(self, new: bool):
        self.__can_play = new
        self.ui.setCheckable(new)
        self.ui.setProperty("fileNotPlayable", not new)
        self.ui.style().unpolish(self.ui)
        self.ui.style().polish(self.ui)

    # is_plaing
    @property
    def is_plaing(self) -> bool:
        """Returns True, if playing a media file else False."""
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            return True
        else:
            False

    # startTime
    @property
    def startTime(self) -> int:
        """
        Controls where to start on the media file. 
        Holds the start time in milliseconds. Must be a int greater or equal to 0.
        Defaults to 0, the start of the media file.
        """
        return self._startTime

    @startTime.setter
    def startTime(self, new: int):
        if isinstance(new, int):
            if new >= 0:
                log.debug(f"Setting start time of key '{self.key}' to '{new}' ms.")
                self._startTime = new
            else:
                log.error(f"Start time must be a positive int.")
        else:
            log.error(f"Start time must be a positive int.")


    # stopTime
    @property
    def stopTime(self) -> int:
        """
        Controls when to stop the playback.
        Must be a int in milliseconds greater or equal to 0 where 0 means end of file.
        Defaults to 0.
        """
        return self._stopTime

    @stopTime.setter
    def stopTime(self, new: int):
        if isinstance(new, int):
            if new >= 0:
                log.debug(f"Setting stop time of key '{self.key}' to '{new}' ms.")
                self._stopTime = new
            else:
                log.error(f"Stop time must be a positive int or 0 for end of file.")
        else:
            log.error(f"Stop time must be a positive int or 0 for end of file.")




    #  METHODES
    # ----------
    def play(self) -> bool:
        """Trys to start playing. Returns True and plays when possible, else returns False."""
        if self._can_play:
            if not self.is_plaing:
                log.info(f"Key '{self.key}' starts playing (file: '{self.path}')")
                self._player.setPosition(self.startTime)
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

    def _auto_stop(self, time):
        """Stops the media, if media position is over stopTime."""
        if not self.stopTime == KeyButton.END_OF_FILE_TIME:
            if time >= self.stopTime:
                self.stop()


    def togglePlay(self):
        """Toggles playing."""
        if self.is_plaing:
            self.stop()
        else:
            self.play()


    def updateSettings(
        self,
        *,
        path = DEFAULT_PATH,
        label = DEFAULT_LABEL,
        startTime = DEFAULT_START_TIME,
        stopTime = DEFAULT_STOP_TIME,
        **kwargs):
        """
        Updates the object according to given settings.
        If settings are not given, uses the defaults.
        """
        self.path = path
        self.label = label
        self.startTime = startTime
        self.stopTime = stopTime


    def getSettings(self):
        """Returns attributes changeble by the user as a dict."""
        return {
            "path": self.path,
            "label": self.label,
            "startTime": self.startTime,
            "stopTime": self.stopTime
        }

    def new(self):
        """Sets everything to default values."""
        self.path = KeyButton.DEFAULT_PATH
        self.label = KeyButton.DEFAULT_LABEL
        self.startTime = KeyButton.DEFAULT_START_TIME
        self.stopTime = KeyButton.DEFAULT_STOP_TIME
        

    @Slot()
    def _openSettingsDialog(self):
        """Opens the Settings Dialog."""
        self.ui.openSettingsDialog.emit(self.key, self.getSettings())



# ########################################
#               PUSHBUTTON
# ########################################
class PushButton(QPushButton):
    
    # Signals
    left_duble_click = Signal()
    openSettingsDialog = Signal(
        str,    # key
        dict,   # settings
    )

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

        # Set attributes
        self._lastDir = Path()

        for row_i, row in enumerate(KEYBOARD_LAYOUT):
            for char_i, char in enumerate(row):
                if char is not None:
                    setattr(self, f'key_{char}', KeyButton(self, char))
                    key: KeyButton = getattr(self, f'key_{char}')
                    layout.addWidget(key.ui, row_i, char_i)
                    self._key_list.append(char)

                    # KeySettingsDialog
                    key.ui.openSettingsDialog.connect(self.openSettingsDialog)

        self.setLayout(layout)


    def getSettings(self):
        return {key: getattr(self, f'key_{key}').getSettings() for key in self._key_list}


    @Slot(str, dict)
    @Slot(str, dict, dict)
    @Slot(dict)
    def updateSettings(self, key=None, values=None, **kwargs):
        """Updates the settings accordingly"""
        for k, v in kwargs.items():
            getattr(self, f'key_{k}').updateSettings(**v)
            try:
                path = Path(v["path"])
                if not path == Path():
                    self._lastDir = path.parent
            except KeyError:
                pass
        if key is not None:
            if values is not None:
                getattr(self, f'key_{key}').updateSettings(**values)
                try:
                    path = Path(values["path"])
                    if not path == Path():
                        self._lastDir = path.parent
                except KeyError:
                    pass
            else:
                raise SyntaxError("Setting key and value without the other is not allowed")


    def new(self):
        """Sets everything to default values."""
        for k in self._key_list:
            getattr(self, f'key_{k}').new()


    @Slot(str, dict)
    def openSettingsDialog(self, key, settings):
        """Opens the Settings Dialog."""
        dlg = KeySettingsDialog(
            self, 
            key,
            self._lastDir,
            **settings
        )

        dlg.dialog_accepted.connect(self.updateSettings)
        dlg.exec()
