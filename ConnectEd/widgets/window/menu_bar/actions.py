from typing import Self

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QKeySequence

from ....app import logger, window

from ....core.check import checked
from ....core.defs  import MIME_TYPE

from ....widgets.graphics.views.diagram  import DiagramView
from ....widgets.graphics.scenes.diagram import DiagramScene

from ...action  import Action

from ..sub_window import DocSubWindow

from .slots import Slots


class Actions:
    _scene  : DiagramScene | None

    @checked
    def __init__(self : Self, slots : Slots) -> None:
        self._scene = None
        SK = QKeySequence.StandardKey  # noqa E806

        # actions for main menus
        self.fileNew            = Action( window(), "New..."        , "Create a new document"               , "Ctrl+N"                     )  # noqa E501
        self.fileOpen           = Action( window(), "Open..."       , "Open document"                       , "Ctrl+O"                     )  # noqa E501
        self.fileSave           = Action( window(), "Save"          , "Save document"                       , "Ctrl+S"                     )  # noqa E501
        self.fileSaveAs         = Action( window(), "Save As..."    , "Save document as"                    , None                         )  # noqa E501
        self.fileClose          = Action( window(), "Close"         , "Close database"                      , None                         )  # noqa E501
        self.fileOpenMRU1       = Action( window(), "&1:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU2       = Action( window(), "&2:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU3       = Action( window(), "&3:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU4       = Action( window(), "&4:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU5       = Action( window(), "&5:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU6       = Action( window(), "&6:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU7       = Action( window(), "&7:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU8       = Action( window(), "&8:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileOpenMRU9       = Action( window(), "&9:"           , "Open recent document"                , None                         )  # noqa E501
        self.fileExit           = Action( window(), "Exit"          , "Exit the application"                , SK.Quit                      )  # noqa E501
        self.editCancel         = Action( window(), "Cancel"        , "Cancel current operation"            , SK.Cancel                    )  # noqa E501
        self.editUndo           = Action( window(), "Undo"          , "Undo"                                , SK.Undo                      )  # noqa E501
        self.editRedo           = Action( window(), "Redo"          , "Redo"                                , SK.Redo                      )  # noqa E501
        self.editCut            = Action( window(), "Cut"           , "Cut"                                 , SK.Cut                       )  # noqa E501
        self.editCopy           = Action( window(), "Copy"          , "Copy"                                , SK.Copy                      )  # noqa E501
        self.editPaste          = Action( window(), "Paste"         , "Paste"                               , SK.Paste                     )  # noqa E501
        self.editDelete         = Action( window(), "Delete"        , "Delete"                              , SK.Delete                    )  # noqa E501
        self.editDuplicate      = Action( window(), "Duplicate"     , "Duplicate"                           , "Ctrl+D"                     )  # noqa E501
        self.editSelectArea     = Action( window(), "Select Area"   , "Select area"                         , None                         )  # noqa E501
        self.editSelectAll      = Action( window(), "Select All"    , "Select all"                          , SK.SelectAll                 )  # noqa E501
        self.editProperties     = Action( window(), "Properties..." , "Edit properties of selected item(s)" , None                         )  # noqa E501
        self.editAppearance     = Action( window(), "Appearance..." , "Edit appearance of selected item(s)" , None                         )  # noqa E501
        self.editQuery          = Action( window(), "Query"         , "Query"                               , "Ctrl+Q"                     )  # noqa E501
        self.viewZoomAll        = Action( window(), "Zoom All"      , "Zoom to fit all"                     , "Ctrl+Home"                  )  # noqa E501
        self.viewZoomSheet      = Action( window(), "Zoom Sheet"    , "Zoom to fit sheet"                   , "Ctrl+Shift+S"               )  # noqa E501
        self.viewZoomArea       = Action( window(), "Zoom Area"     , "Zoom to area"                        , "Ctrl+Shift+W"               )  # noqa E501
        self.viewZoomIn         = Action( window(), "Zoom In"       , "Zoom in"                             , "Ctrl++"                     )  # noqa E501
        self.viewZoomOut        = Action( window(), "Zoom Out"      , "Zoom out"                            , "Ctrl+-"                     )  # noqa E501
        self.viewPan            = Action( window(), "Pan"           , "Pan"                                 , None                         )  # noqa E501
        self.viewPanUp          = Action( window(), "Pan Up"        , "Pan up"                              , "Ctrl+Up"                    )  # noqa E501
        self.viewPanDown        = Action( window(), "Pan Down"      , "Pan down"                            , "Ctrl+Down"                  )  # noqa E501
        self.viewPanLeft        = Action( window(), "Pan Left"      , "Pan left"                            , "Ctrl+Left"                  )  # noqa E501
        self.viewPanRight       = Action( window(), "Pan Right"     , "Pan right"                           , "Ctrl+Right"                 )  # noqa E501
        self.viewGridDisplay    = Action( window(), "Grid Display"  , "Toggle grid display"                 , "Ctrl+G"       , True , True )  # noqa E501
        self.viewGridSnap       = Action( window(), "Grid Snap"     , "Toggle grid snap"                    , "Ctrl+Shift+G" , True , True )  # noqa E501
        self.viewThemeDark      = Action( window(), "Dark"          , "Set dark theme"                      , None                         )  # noqa E501
        self.viewThemeLightMono = Action( window(), "Light Mono"    , "Set light mono theme"                , None                         )  # noqa E501
        self.placePort          = Action( window(), "Port"          , "Place Port"                          , "Ctrl+I"                     )  # noqa E501
        self.placeGate          = Action( window(), "Gate"          , "Place Gate"                          , "Ctrl+G"                     )  # noqa E501
        self.placeBlock         = Action( window(), "Block"         , "Place Block"                         , "Ctrl+B"                     )  # noqa E501
        self.placeBlockPin      = Action( window(), "Block Pin"     , "Place Block Pin"                     , "Ctrl+P"                     )  # noqa E501
        self.placeSymbolPin     = Action( window(), "Pin"           , "Place Symbol Pin"                    , "Ctrl+P"                     )  # noqa E501
        self.placeConnection    = Action( window(), "Connection"    , "Place Connection"                    , "C"                          )  # noqa E501
        self.placeTap           = Action( window(), "Tap"           , "Place Tap"                           , "T"                          )  # noqa E501
        self.placeNetLabel      = Action( window(), "Net Label"     , "Place Net Label"                     , "N"                          )  # noqa E501
        self.placeLine          = Action( window(), "Line"          , "Place Line"                          , "Ctrl+L"                     )  # noqa E501
        self.placeRectangle     = Action( window(), "Rectangle"     , "Place Rectangle"                     , "Ctrl+R"                     )  # noqa E501
        self.placeEllipse       = Action( window(), "Ellipse"       , "Place Ellipse"                       , "Ctrl+E"                     )  # noqa E501
        self.placePolyline      = Action( window(), "Polyline"      , "Place Polyline"                      , "Ctrl+M"                     )  # noqa E501
        self.placeText          = Action( window(), "Text"          , "Place Text"                          , "Ctrl+T"                     )  # noqa E501
        self.windowNavigator    = Action( window(), "Navigator"     , "Show the navigator window"           , None                         )  # noqa E501
        self.windowMessages     = Action( window(), "Messages"      , "Show the messages window"            , None                         )  # noqa E501
        self.windowTranscript   = Action( window(), "Transcript"    , "Show the transcript window"          , None                         )  # noqa E501
        self.windowLog          = Action( window(), "Log"           , "Show the log window"                 , None                         )  # noqa E501
        self.aiSettings         = Action( window(), "Settings"      , "Configure AI providers"              , None                         )  # noqa E501
        self.windowNext         = Action( window(), "Next"          , "Next"                                , "Ctrl+F6"                    )  # noqa E501
        self.windowPrevious     = Action( window(), "Previous"      , "Previous"                            , "Ctrl+Shift+F6"              )  # noqa E501
        self.helpAbout          = Action( window(), "About"         , ""                                    , "Ctrl+Shift+T"               )  # noqa E501

        # shortcut keys for view actions
        self.editRotateCW       = Action( window(), "Rotate CW"    , "Rotate clockwise"                     , "]"                          )  # noqa E501
        self.editRotateCCW      = Action( window(), "Rotate CCW"   , "Rotate counterclockwise"              , "["                          )  # noqa E501

        # slot connections
        self.fileNew            .triggered.connect(slots.fileNew)
        self.fileOpen           .triggered.connect(slots.fileOpen)
        self.fileSave           .triggered.connect(slots.fileSave)
        self.fileSaveAs         .triggered.connect(slots.fileSaveAs)
        self.fileClose          .triggered.connect(slots.fileClose)
        self.fileOpenMRU1       .triggered.connect(slots.fileOpenMRU1)
        self.fileOpenMRU2       .triggered.connect(slots.fileOpenMRU2)
        self.fileOpenMRU3       .triggered.connect(slots.fileOpenMRU3)
        self.fileOpenMRU4       .triggered.connect(slots.fileOpenMRU4)
        self.fileOpenMRU5       .triggered.connect(slots.fileOpenMRU5)
        self.fileOpenMRU6       .triggered.connect(slots.fileOpenMRU6)
        self.fileOpenMRU7       .triggered.connect(slots.fileOpenMRU7)
        self.fileOpenMRU8       .triggered.connect(slots.fileOpenMRU8)
        self.fileOpenMRU9       .triggered.connect(slots.fileOpenMRU9)
        self.fileExit           .triggered.connect(slots.fileExit)
        self.editCancel         .triggered.connect(slots.editCancel)
        self.editUndo           .triggered.connect(slots.editUndo)
        self.editRedo           .triggered.connect(slots.editRedo)
        self.editCut            .triggered.connect(slots.editCut)
        self.editCopy           .triggered.connect(slots.editCopy)
        self.editPaste          .triggered.connect(slots.editPaste)
        self.editDelete         .triggered.connect(slots.editDelete)
        self.editDuplicate      .triggered.connect(slots.editDuplicate)
        self.editSelectArea     .triggered.connect(slots.editSelectArea)
        self.editSelectAll      .triggered.connect(slots.editSelectAll)
        self.editProperties     .triggered.connect(slots.editProperties)
        self.editAppearance     .triggered.connect(slots.editAppearance)
        self.editQuery          .triggered.connect(slots.editQuery)
        self.editRotateCW       .triggered.connect(slots.editRotateCW)
        self.editRotateCCW      .triggered.connect(slots.editRotateCCW)
        self.viewZoomAll        .triggered.connect(slots.viewZoomAll)
        self.viewZoomSheet      .triggered.connect(slots.viewZoomSheet)
        self.viewZoomArea       .triggered.connect(slots.viewZoomArea)
        self.viewZoomIn         .triggered.connect(slots.viewZoomIn)
        self.viewZoomOut        .triggered.connect(slots.viewZoomOut)
        self.viewPan            .triggered.connect(slots.viewPan)
        self.viewPanUp          .triggered.connect(slots.viewPanUp)
        self.viewPanDown        .triggered.connect(slots.viewPanDown)
        self.viewPanLeft        .triggered.connect(slots.viewPanLeft)
        self.viewPanRight       .triggered.connect(slots.viewPanRight)
        self.viewGridDisplay    .triggered.connect(slots.viewGridDisplay)
        self.viewGridSnap       .triggered.connect(slots.viewGridSnap)
        self.viewThemeDark      .triggered.connect(slots.viewThemeDark)
        self.viewThemeLightMono .triggered.connect(slots.viewThemeLightMono)
        self.placePort          .triggered.connect(slots.placePort)
        self.placeGate          .triggered.connect(slots.placeGate)
        self.placeBlock         .triggered.connect(slots.placeBlock)
        self.placeBlockPin      .triggered.connect(slots.placeBlockPin)
        self.placeSymbolPin     .triggered.connect(slots.placeSymbolPin)
        self.placeConnection    .triggered.connect(slots.placeConnection)
        self.placeTap           .triggered.connect(slots.placeTap)
        self.placeNetLabel      .triggered.connect(slots.placeNetLabel)
        self.placeLine          .triggered.connect(slots.placeLine)
        self.placeRectangle     .triggered.connect(slots.placeRectangle)
        self.placeEllipse       .triggered.connect(slots.placeEllipse)
        self.placePolyline      .triggered.connect(slots.placePolyline)
        self.placeText          .triggered.connect(slots.placeText)
        self.windowNavigator    .triggered.connect(slots.windowNavigator)
        self.windowMessages     .triggered.connect(slots.windowMessages)
        self.windowTranscript   .triggered.connect(slots.windowTranscript)
        self.windowLog          .triggered.connect(slots.windowLog)
        self.aiSettings         .triggered.connect(slots.aiSettings)
        self.windowNext         .triggered.connect(slots.windowNext)
        self.windowPrevious     .triggered.connect(slots.windowPrevious)
        self.helpAbout          .triggered.connect(slots.helpAbout)

        # finish up
        self.onSubWindowActivated(None)
        window().mdiArea().subWindowActivated.connect(self.onSubWindowActivated)
        clipboard = QApplication.clipboard()
        if clipboard is None:
            raise RuntimeError("No clipboard")
        clipboard.dataChanged.connect(self.onClipboardDataChanged)


    def actionEnable(self : Self, name : str, enable : bool) -> None:
        getattr(self, name).setEnabled(enable)

    def onSubWindowActivated(
        self      : Self,
        subwindow : DocSubWindow | None
    ) -> None:
        # disconnect previous signals
        s = self._scene
        if s is not None:
            try:
                s.selectionChanged.disconnect(self.onSelectionChanged)
                s.undo_stack.canUndoChanged.disconnect(self.onCanUndoChanged)
                s.undo_stack.canRedoChanged.disconnect(self.onCanRedoChanged)
            except RuntimeError: # workaround for Qt cleanup
                pass
        scene = None
        if isinstance(subwindow, DocSubWindow):
            widget = subwindow.widget()
            if isinstance(widget, DiagramView):
                scene = widget.scene()
                if isinstance(scene, DiagramScene):
                    self._scene = scene
                    self.onCanUndoChanged(scene.undo_stack.canUndo())
                    self.onCanRedoChanged(scene.undo_stack.canRedo())
                    self.onSelectionChanged()
                    self.onClipboardDataChanged()
                else:
                    logger().warning("Bad scene")
                    self._scene = None
            else:
                logger().warning("Bad widget")
                self._scene = None
        en = scene is not None
        self.fileSave        .setEnabled(en)
        self.fileSaveAs      .setEnabled(en)
        self.editDuplicate   .setEnabled(en)
        self.editAppearance  .setEnabled(en)
        self.viewZoomAll     .setEnabled(en)
        self.viewZoomSheet   .setEnabled(en)
        self.viewZoomArea    .setEnabled(en)
        self.viewZoomIn      .setEnabled(en)
        self.viewZoomOut     .setEnabled(en)
        self.viewPan         .setEnabled(en)
        self.viewPanUp       .setEnabled(en)
        self.viewPanDown     .setEnabled(en)
        self.viewPanLeft     .setEnabled(en)
        self.viewPanRight    .setEnabled(en)
        self.viewGridDisplay .setEnabled(en)
        self.viewGridSnap    .setEnabled(en)
        self.placeBlock      .setEnabled(en)
        self.placeRectangle  .setEnabled(en)
        self.placeText       .setEnabled(en)
        if scene is not None:
            # connect signals
            scene.selectionChanged.connect(self.onSelectionChanged)
            scene.undo_stack.canUndoChanged.connect(self.onCanUndoChanged)
            scene.undo_stack.canRedoChanged.connect(self.onCanRedoChanged)
            self.onClipboardDataChanged()
            self.onSelectionChanged()
        self._scene = scene

    def onSelectionChanged(self : Self) -> None:
        try:
            scene = self._scene
            n = len(scene.selectedItems()) if scene is not None else 0
            self.editCut        .setEnabled( n > 0 )
            self.editCopy       .setEnabled( n > 0 )
            self.editDelete     .setEnabled( n > 0 )
            self.editDuplicate  .setEnabled( n > 0 )
            self.editAppearance .setEnabled( n > 0 )
        except (RuntimeError, AttributeError): # workaround for Qt cleanup
            pass

    def onClipboardDataChanged(self : Self) -> None:
        clipboard = QApplication.clipboard()
        if clipboard is None:
            raise RuntimeError("No clipboard")
        mime_data = clipboard.mimeData()
        self.editPaste.setEnabled(
            mime_data is not None and mime_data.hasFormat(MIME_TYPE)
        )

    def onCanUndoChanged(self : Self, canUndo : bool) -> None:  # noqa E803
        self.editUndo.setEnabled(canUndo)

    def onCanRedoChanged(self : Self, canRedo : bool) -> None:  # noqa E803
        self.editRedo.setEnabled(canRedo)

# TODO control status of edit cancel/complete
