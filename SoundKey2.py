import logging
from pathlib import Path
import sys

import PySide6
from PySide6.QtWidgets import QApplication, QMainWindow

from keyboard import Keyboard
from show import Show
from ui.uic.ui_mainWindow import Ui_MainWindow


STYLE_SHEET_PATH = Path(__name__).parent / "styleSheet.css"

# Logging
log = logging.getLogger(__name__)
log.root.setLevel(logging.DEBUG)
logging_stream_handler = logging.StreamHandler()
logging_stream_handler.setLevel(logging.DEBUG)
logging_formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s: %(message)s')
logging_stream_handler.setFormatter(logging_formatter)
log.root.addHandler(logging_stream_handler)


# ===============================
#           MainWindow
# ===============================
class MainWindow(QMainWindow):
    
    def __init__(self) -> None:
        super(MainWindow, self).__init__()


        # Setup generated ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.loadStyleSheet()

        # Create Show object
        self.show_ = Show(self.ui.keyboardHolder)

        self.ui.actionOpenShow.triggered.connect(self.show_.load_gui)
        self.ui.actionSaveShow.triggered.connect(self.show_.save)
        self.ui.actionSaveShowAs.triggered.connect(self.show_.save_gui)
        self.ui.actionNewShow.triggered.connect(self.show_.new)
        self.ui.actionExit.triggered.connect(self.close)


    def loadStyleSheet(self):
        log.info(f"Loading StyleSheet '{STYLE_SHEET_PATH}'")
        with STYLE_SHEET_PATH.open('r') as f_style_scheet:
            self.setStyleSheet(str(f_style_scheet.read()))


# ===============================
#           __MAIN__
# ===============================
if __name__ == "__main__":
    # Start Logging
    log.info("App starting.")
    log.info(f"PySide version: {PySide6.__version__}")

    # Create Application
    app = QApplication(sys.argv)

    # Create main Window
    main_window = MainWindow()

    main_window.show()

    sys.exit(app.exec())
