# Show class to hold settings for one show.
# Author 9qUmV4

SHOW_SAVE_FILE_VERSION = "0.1.0"

import json
import logging
from os import PathLike
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Slot

from .keyboard import Keyboard


log = logging.getLogger(__name__)

class Show:


    def __init__(self, keyboard_parent) -> None:
        self._show = {}
        self._path = Path()      # Path to save file
        
        self.keyboard = Keyboard(keyboard_parent)


    def load(self, path: PathLike):
        self._path = Path(path)
        log.info(f"Loading Show file '{self._path}'")
        with self._path.open('r') as f_show:
            show = json.load(f_show)

        self._show = show
        self.keyboard.updateSettings(**show["keyboard"])


    def new(self):
        log.info("Loading new Show")
        self._show = {}
        self._path = Path()
        self.keyboard.new()
        log.info("Suceccfully loaded new Show")


    @Slot()
    def load_gui(self):
        file_path, _ = QFileDialog.getOpenFileName(
            caption="Open Show",
            dir=str(self._path.parent),
            filter="SoundKey File (*.SoundKey);;Any (*)",
        )
        if file_path == "":
            log.info("File dialog 'Open Show' canceled by user")
            return None
        else:
            file_path = Path(file_path)
            log.debug(f"File dialog 'Open Show' closed returning '{file_path}'")
            self.load(file_path)


    def save(
        self,
        ):
        if self._can_save:
            self._show["version"] = SHOW_SAVE_FILE_VERSION
            self._show["keyboard"] = self.keyboard.getSettings()

            log.info(f"Creating SoundKey file: '{self._path}'")
            with self._path.open('w') as f_show:
                log.info(f"Creating json")
                d_show = ShowEncoder().encode(self._show)
                log.info(f"Writing data to file")
                f_show.write(d_show)

            log.info(f"Saved show suceccfully")
        
        else:
            log.error("Can not save, no save path exists")

        

    def save_gui(self, **kwargs):
        file_path, _ = QFileDialog.getSaveFileName(
            caption="Save Show",
            dir=str(self._path.parent),
            filter="SoundKey File (*.SoundKey);;Any (*)",
        )
        if file_path == "":
            log.info("File dialog 'Open Show' canceled by user")
            return None
        else:
            file_path = Path(file_path)
            log.debug(f"File dialog 'Open Show' closed returning '{file_path}'")
        # TODO Check filepath
        self._path = Path(file_path)
        self.save(**kwargs)

    #  PROPERTIES
    # ------------
    @property
    def _path(self) -> Path:
        return self.__path
    
    @_path.setter
    def _path(self, new: PathLike | str):
        new = Path(new)
        log.info(f"New save path: '{new}'")
        self.__path = new
        self._can_save = new.is_file()


class ShowEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return super().default(o)




