#rom enum import Enum, auto
#
#
#lass CanvasModeMixin:
#   class ModeDuration(Enum):
#       MOMENTARY = auto()
#       PERSISTENT = auto()
#
#   class Mode:
#       SELECT         = auto()
#       PLACE_BLOCK    = auto()
#       PLACE_PIN      = auto()
#       PLACE_WIRE     = auto()
#       PLACE_TAP      = auto()
#       PLACE_JUNCTION = auto()
#       PLACE_PORT     = auto()
#       PLACE_CODE     = auto()
#       PLACE_LINE     = auto()
#       PLACE_RECT     = auto()
#       PLACE_POLY     = auto()
#       PLACE_ARC      = auto()
#       PLACE_ELLIPSE  = auto()
#       PLACE_TEXT     = auto()
#       PLACE_IMAGE    = auto()
#
#   def setMode(self, mode):
#       self.mode = mode
#       match mode:
#           case self.Mode.SELECT:         t = 'Select'
#           case self.Mode.SELECT_AREA:    t = 'Select Area'
#           case self.Mode.PLACE_BLOCK:    t = 'Place Block'
#           case self.Mode.PLACE_PIN:      t = 'Place Pin'
#           case self.Mode.PLACE_WIRE:     t = 'Place Wire'
#           case self.Mode.PLACE_TAP:      t = 'Place Tap'
#           case self.Mode.PLACE_JUNCTION: t = 'Place Junction'
#           case self.Mode.PLACE_PORT:     t = 'Place Port'
#           case self.Mode.PLACE_CODE:     t = 'Place Code'
#           case self.Mode.PLACE_LINE:     t = 'Place Line'
#           case self.Mode.PLACE_RECT:     t = 'Place Rectangle'
#           case self.Mode.PLACE_POLY:     t = 'Place PolyLine'
#           case self.Mode.PLACE_ARC:      t = 'Place Arc'
#           case self.Mode.PLACE_ELLIPSE:  t = 'Place Ellipse'
#           case self.Mode.PLACE_TEXT:     t = 'Place Text'
#           case self.Mode.PLACE_IMAGE:    t = 'Place Image'
#       self.window().statusBar.mode.setText(t)
#       self.window().statusBar.update()