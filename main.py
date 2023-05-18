import sys

from PyQt5.QtWidgets import *

from Bmvs_login import Login

def main():
    app = QApplication(sys.argv)
    login_window = Login()
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()