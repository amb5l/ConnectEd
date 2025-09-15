from typing import Self, Optional

from PyQt6.QtWidgets import QApplication, QMdiSubWindow
from PyQt6.QtGui     import QKeySequence

from ...app import logger, window

from ...core.defs import MIME_TYPE

from ...widgets.graphics.views.drawing  import DrawingSubWindow
from ...widgets.graphics.scenes.drawing import DrawingScene

from ..private  import Action


class Actions:
    _scene  : Optional[DrawingScene]

    def __init__(self : Self) -> None:
        self._scene  = None
        SK = QKeySequence.StandardKey

        self.fileNewDesign      = Action( window(), "Design"        , "Create a new design"                    , "Ctrl+N"                     )
        self.fileNewLibrary     = Action( window(), "Library"       , "Create a new library"                   , None                         )
        self.fileOpen           = Action( window(), "Open"          , "Open database"                          , "Ctrl+O"                     )
        self.fileSave           = Action( window(), "Save"          , "Save database"                          , "Ctrl+S"                     )
        self.fileSaveAs         = Action( window(), "Save As"       , "Save database as"                       , None                         )
        self.fileExit           = Action( window(), "Exit"          , "Exit the application"                   , SK.Quit                      )
        self.editUndo           = Action( window(), "Undo"          , "Undo"                                   , SK.Undo                      )
        self.editRedo           = Action( window(), "Redo"          , "Redo"                                   , SK.Redo                      )
        self.editCut            = Action( window(), "Cut"           , "Cut"                                    , SK.Cut                       )
        self.editCopy           = Action( window(), "Copy"          , "Copy"                                   , SK.Copy                      )
        self.editPaste          = Action( window(), "Paste"         , "Paste"                                  , SK.Paste                     )
        self.editDelete         = Action( window(), "Delete"        , "Delete"                                 , SK.Delete                    )
        self.editDuplicate      = Action( window(), "Duplicate"     , "Duplicate"                              , "Ctrl+D"                     )
        self.editSelectArea     = Action( window(), "Select Area"   , "Select area"                            , None                         )
        self.editSelectAll      = Action( window(), "Select All"    , "Select all"                             , SK.SelectAll                 )
        self.editProperties     = Action( window(), "Properties..." , "Edit properties of selected element(s)" , None                         )
        self.editAppearance     = Action( window(), "Appearance..." , "Edit appearance of selected element(s)" , None                         )
        self.editQuery          = Action( window(), "Query"         , "Query"                                  , "Ctrl+Q"                     )
        self.viewZoomAll        = Action( window(), "Zoom All"      , "Zoom to fit all"                        , "Ctrl+Home"                  )
        self.viewZoomSheet      = Action( window(), "Zoom Sheet"    , "Zoom to fit sheet"                      , "Ctrl+Shift+S"               )
        self.viewZoomArea       = Action( window(), "Zoom Area"     , "Zoom to area"                           , "Ctrl+Shift+W"               )
        self.viewZoomIn         = Action( window(), "Zoom In"       , "Zoom in"                                , "Ctrl++"                     )
        self.viewZoomOut        = Action( window(), "Zoom Out"      , "Zoom out"                               , "Ctrl+-"                     )
        self.viewPan            = Action( window(), "Pan"           , "Pan"                                    , None                         )
        self.viewPanUp          = Action( window(), "Pan Up"        , "Pan up"                                 , "Ctrl+Up"                    )
        self.viewPanDown        = Action( window(), "Pan Down"      , "Pan down"                               , "Ctrl+Down"                  )
        self.viewPanLeft        = Action( window(), "Pan Left"      , "Pan left"                               , "Ctrl+Left"                  )
        self.viewPanRight       = Action( window(), "Pan Right"     , "Pan right"                              , "Ctrl+Right"                 )
        self.viewGridDisplay    = Action( window(), "Grid Display"  , "Toggle grid display"                    , "Ctrl+G"       , True , True )
        self.viewGridSnap       = Action( window(), "Grid Snap"     , "Toggle grid snap"                       , "Ctrl+Shift+G" , True , True )
        self.viewThemeDark      = Action( window(), "Dark"          , "Set dark theme"                         , None                         )
        self.viewThemeLightMono = Action( window(), "Light Mono"    , "Set light mono theme"                   , None                         )
        self.placePort          = Action( window(), "Port"          , "Place Port"                             , "Ctrl+I"                     )
        self.placeBlock         = Action( window(), "Block"         , "Place Block"                            , "Ctrl+B"                     )
        self.placeBlockPin      = Action( window(), "Block Pin"     , "Place Block Pin"                        , "Ctrl+P"                     )
        self.placeRectangle     = Action( window(), "Rectangle"     , "Place Rectangle"                        , "Ctrl+R"                     )
        self.placeTextBlock     = Action( window(), "Text Block"    , "Place Text Block"                       , "Ctrl+T"                     )
        self.placeText          = Action( window(), "Text"          , "Place Text"                             , "Ctrl+L"                     )
        self.windowExplorer     = Action( window(), "Explorer"      , "Show the explorer window"               , None                         )
        self.windowMessages     = Action( window(), "Messages"      , "Show the messages window"               , None                         )
        self.windowTranscript   = Action( window(), "Transcript"    , "Show the transcript window"             , None                         )
        self.windowLog          = Action( window(), "Log"           , "Show the log window"                    , None                         )
        self.windowNext         = Action( window(), "Next"          , "Next"                                   , "Ctrl+F6"                    )
        self.windowPrevious     = Action( window(), "Previous"      , "Previous"                               , "Ctrl+Shift+F6"              )
        self.helpAbout          = Action( window(), "About"         , ""                                       , "Ctrl+Shift+T"               )

        self.onSubWindowActivated(None)

    def actionEnable(self : Self, name : str, enable : bool) -> None:
        getattr(self, name).setEnabled(enable)

    def onSubWindowActivated(
        self      : Self,
        subwindow : Optional[QMdiSubWindow]
    ) -> None:
        # disconnect previous signals
        s = self._scene
        if s:
            try:
                s.selectionChanged.disconnect(self.onSelectionChanged)
                s.undo_stack.canUndoChanged.disconnect(self.onCanUndoChanged)
                s.undo_stack.canRedoChanged.disconnect(self.onCanRedoChanged)
            except TypeError:
                pass
        en = subwindow is not None and isinstance(subwindow, DrawingSubWindow)
        self._scene = subwindow.widget().scene() if en else None
        self.onCanUndoChanged(en and self._scene.undo_stack.canUndo())
        self.onCanRedoChanged(en and self._scene.undo_stack.canRedo())
        self.onSelectionChanged()
        self.onClipboardDataChanged()
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
        self.placeTextBlock  .setEnabled(en)
        self.placeText   .setEnabled(en)
        if en and self._scene is not None:
            # connect signals
            self._scene.selectionChanged.connect(self.onSelectionChanged)
            self._scene.undo_stack.canUndoChanged.connect(self.onCanUndoChanged)
            self._scene.undo_stack.canRedoChanged.connect(self.onCanRedoChanged)
            self.onClipboardDataChanged()
            self.onSelectionChanged()

    def onSelectionChanged(self : Self) -> None:
        try:
            if self._scene:
                selected_items = self._scene.selectedItems()
                n = len(selected_items)
            else:
                n = 0
            self.editCut        .setEnabled( n > 0 )
            self.editCopy       .setEnabled( n > 0 )
            self.editDelete     .setEnabled( n > 0 )
            self.editDuplicate  .setEnabled( n > 0 )
            self.editAppearance .setEnabled( n > 0 )
        except RuntimeError:
            pass  # Objects deleted during shutdown
        except Exception as e:
            logger().error(f"Exception in onSelectionChanged: {e}")
            import traceback
            traceback.print_exc()

    def onClipboardDataChanged(self : Self) -> None:
        if not self._scene:
            en = False
        else:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            en = mime_data is not None and mime_data.hasFormat(MIME_TYPE)
        self.editPaste.setEnabled(en)

    def onCanUndoChanged(self : Self, canUndo : bool) -> None:
        try:
            self.editUndo.setEnabled(canUndo)
        except RuntimeError:
            pass  # Object deleted during shutdown

    def onCanRedoChanged(self : Self, canRedo : bool) -> None:
        try:
            self.editRedo.setEnabled(canRedo)
        except RuntimeError:
            pass  # Object deleted during shutdown

# TODO control status of edit cancel/complete
