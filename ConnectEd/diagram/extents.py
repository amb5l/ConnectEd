from PyQt6.QtCore import QSettings, QSize

from common import ORG_NAME, APP_NAME, DPI


class DiagramExtents:
    EXTENTS_DEFAULT = { # sheet extents in inches
        "A4": ( 11.69 ,  8.27 ),
        "A3": ( 16.54 , 11.69 ),
        "A2": ( 23.38 , 16.54 ),
        "A1": ( 33.07 , 23.38 ),
        "A0": ( 46.77 , 33.07 ),
        "A":  (  9.70 ,  7.20 ),
        "B":  ( 15.20 ,  9.70 ),
        "C":  ( 20.20 , 15.20 ),
        "D":  ( 32.20 , 20.20 ),
        "E":  ( 42.20 , 32.20 )
    }

    def __init__(self):
        self.extents = {}
        # initialise standard extents
        for k, v in self.EXTENTS_DEFAULT.items():
            self.extents[k + "_LANDSCAPE"] = v
            self.extents[k + "_PORTRAIT"] = (v[1], v[0])
        # attempt to load extents from settings
        settings = QSettings(ORG_NAME, APP_NAME)
        if "extents" in settings.childGroups():
            settings.beginGroup("extents")
            for extentsName in settings.childKeys():
                self.extents[extentsName] = settings.value(extentsName)
            settings.endGroup()

    def __call__(self, name):
        return DPI * QSize(*self.extents[name])

    # TODO write method to save extents to settings
