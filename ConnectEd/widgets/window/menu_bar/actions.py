from typing import Self

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QKeySequence

from ....app import window

from ....core.defs import MIME_TYPE

from ....widgets.graphics.views.drawing  import DrawingView
from ....widgets.graphics.scenes.drawing import DrawingScene

from ...action  import Action

from ..sub_window import SubWindow


class Actions:
    _scene  : DrawingScene | None

    def __init__(self : Self) -> None:
        self._scene  = None
        SK = QKeySequence.StandardKey

        # actions for main menus
        self.fileNewDesign      = Action( window(), "Design"        , "Create a new design"                 , "Ctrl+N"                     )  # noqa E501
        self.fileNewLibrary     = Action( window(), "Library"       , "Create a new library"                , None                         )  # noqa E501
        self.fileOpen           = Action( window(), "Open"          , "Open database"                       , "Ctrl+O"                     )  # noqa E501
        self.fileSave           = Action( window(), "Save"          , "Save database"                       , "Ctrl+S"                     )  # noqa E501
        self.fileSaveAs         = Action( window(), "Save As"       , "Save database as"                    , None                         )  # noqa E501
        self.fileClose          = Action( window(), "Close"         , "Close database"                      , None                         )  # noqa E501
        self.fileOpenMRU1       = Action( window(), "&1:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU2       = Action( window(), "&2:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU3       = Action( window(), "&3:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU4       = Action( window(), "&4:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU5       = Action( window(), "&5:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU6       = Action( window(), "&6:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU7       = Action( window(), "&7:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU8       = Action( window(), "&8:"           , "Open recent file"                    , None                         )  # noqa E501
        self.fileOpenMRU9       = Action( window(), "&9:"           , "Open recent file"                    , None                         )  # noqa E501
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
        self.placeLine          = Action( window(), "Line"          , "Place Line"                          , "Ctrl+L"                     )  # noqa E501
        self.placeRectangle     = Action( window(), "Rectangle"     , "Place Rectangle"                     , "Ctrl+R"                     )  # noqa E501
        self.placeEllipse       = Action( window(), "Ellipse"       , "Place Ellipse"                       , "Ctrl+E"                     )  # noqa E501
        self.placePolyline      = Action( window(), "Polyline"      , "Place Polyline"                      , "Ctrl+M"                     )  # noqa E501
        self.placeText          = Action( window(), "Text"          , "Place Text"                          , "Ctrl+T"                     )  # noqa E501
        self.windowNavigator    = Action( window(), "Navigator"     , "Show the navigator window"           , None                         )  # noqa E501
        self.windowMessages     = Action( window(), "Messages"      , "Show the messages window"            , None                         )  # noqa E501
        self.windowTranscript   = Action( window(), "Transcript"    , "Show the transcript window"          , None                         )  # noqa E501
        self.windowLog          = Action( window(), "Log"           , "Show the log window"                 , None                         )  # noqa E501
        self.windowNext         = Action( window(), "Next"          , "Next"                                , "Ctrl+F6"                    )  # noqa E501
        self.windowPrevious     = Action( window(), "Previous"      , "Previous"                            , "Ctrl+Shift+F6"              )  # noqa E501
        self.helpAbout          = Action( window(), "About"         , ""                                    , "Ctrl+Shift+T"               )  # noqa E501

        # shortcut keys for view actions
        self.editRotateCW       = Action( window(), "Rotate CW"    , "Rotate clockwise"                     , "]"                          )  # noqa E501
        self.editRotateCCW      = Action( window(), "Rotate CCW"   , "Rotate counterclockwise"              , "["                          )  # noqa E501

        self.onSubWindowActivated(None)
        window().mdiArea().subWindowActivated.connect(self.onSubWindowActivated)
        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self.onClipboardDataChanged)


    def actionEnable(self : Self, name : str, enable : bool) -> None:
        getattr(self, name).setEnabled(enable)

    def onSubWindowActivated(
        self      : Self,
        subwindow : SubWindow | None
    ) -> None:
        # disconnect previous signals
        s = self._scene
        if s:
            try:
                s.selectionChanged.disconnect(self.onSelectionChanged)
                s.undo_stack.canUndoChanged.disconnect(self.onCanUndoChanged)
                s.undo_stack.canRedoChanged.disconnect(self.onCanRedoChanged)
            except: # workaround for Qt cleanup
                pass
        self._scene = None
        view : DrawingView | None = subwindow.widget() if subwindow else None
        self._scene : DrawingScene | None = view.scene() \
            if subwindow and view else None
        self.onCanUndoChanged(bool(self._scene and self._scene.undo_stack.canUndo()))
        self.onCanRedoChanged(bool(self._scene and self._scene.undo_stack.canRedo()))
        self.onSelectionChanged()
        self.onClipboardDataChanged()
        self.fileSave        .setEnabled(bool(self._scene))
        self.fileSaveAs      .setEnabled(bool(self._scene))
        self.editDuplicate   .setEnabled(bool(self._scene))
        self.editAppearance  .setEnabled(bool(self._scene))
        self.viewZoomAll     .setEnabled(bool(self._scene))
        self.viewZoomSheet   .setEnabled(bool(self._scene))
        self.viewZoomArea    .setEnabled(bool(self._scene))
        self.viewZoomIn      .setEnabled(bool(self._scene))
        self.viewZoomOut     .setEnabled(bool(self._scene))
        self.viewPan         .setEnabled(bool(self._scene))
        self.viewPanUp       .setEnabled(bool(self._scene))
        self.viewPanDown     .setEnabled(bool(self._scene))
        self.viewPanLeft     .setEnabled(bool(self._scene))
        self.viewPanRight    .setEnabled(bool(self._scene))
        self.viewGridDisplay .setEnabled(bool(self._scene))
        self.viewGridSnap    .setEnabled(bool(self._scene))
        self.placeBlock      .setEnabled(bool(self._scene))
        self.placeRectangle  .setEnabled(bool(self._scene))
        self.placeText       .setEnabled(bool(self._scene))
        if self._scene:
            # connect signals
            self._scene.selectionChanged.connect(self.onSelectionChanged)
            self._scene.undo_stack.canUndoChanged.connect(self.onCanUndoChanged)
            self._scene.undo_stack.canRedoChanged.connect(self.onCanRedoChanged)
            self.onClipboardDataChanged()
            self.onSelectionChanged()

    def onSelectionChanged(self : Self) -> None:
        try:
            selected_items = self._scene.selectedItems()
            n = len(selected_items)
            self.editCut        .setEnabled( n > 0 )
            self.editCopy       .setEnabled( n > 0 )
            self.editDelete     .setEnabled( n > 0 )
            self.editDuplicate  .setEnabled( n > 0 )
            self.editAppearance .setEnabled( n > 0 )
        except (RuntimeError, AttributeError): # workaround for Qt cleanup
            pass

    def onClipboardDataChanged(self : Self) -> None:
        mime_data = QApplication.clipboard().mimeData()
        self.editPaste.setEnabled(
            self._scene is not None and \
            mime_data is not None and \
            mime_data.hasFormat(MIME_TYPE)
        )

    def onCanUndoChanged(self : Self, canUndo : bool) -> None:
        self.editUndo.setEnabled(canUndo)

    def onCanRedoChanged(self : Self, canRedo : bool) -> None:
        self.editRedo.setEnabled(canRedo)

# TODO control status of edit cancel/complete
