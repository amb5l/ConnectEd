from PyQt6.QtCore import QSettings
from ConnectEd.constants import ORGNAME, APPNAME

settings = QSettings(ORGNAME, APPNAME)
settings.clear()
