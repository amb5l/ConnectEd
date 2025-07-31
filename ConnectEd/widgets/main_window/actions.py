from typing import Self, Optional

from PyQt6.QtWidgets import QApplication, QMdiSubWindow, QGraphicsItem
from PyQt6.QtGui     import QKeySequence

from ...core    import MIME_TYPE, logger
from ...widgets import DrawingSubWindow, DrawingScene
from ..private  import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..main_window import MainWindow


class Actions:
    _parent : "MainWindow"
    _scene  : Optional[DrawingScene]

    def __init__(self : Self, parent : "MainWindow") -> None:
        self._parent = parent
        self._scene  = None
        SK = QKeySequence.StandardKey

        self.fileNewDesign      = Action( self._parent, "Design"        , "Create a new design"                    , "Ctrl+N"                     )
        self.fileNewLibrary     = Action( self._parent, "Library"       , "Create a new library"                   , None                         )
        self.fileOpen           = Action( self._parent, "Open"          , "Open database"                          , "Ctrl+O"                     )
        self.fileSave           = Action( self._parent, "Save"          , "Save database"                          , "Ctrl+S"                     )
        self.fileSaveAs         = Action( self._parent, "Save As"       , "Save database as"                       , None                         )
        self.fileExit           = Action( self._parent, "Exit"          , "Exit the application"                   , SK.Quit                      )
        self.editUndo           = Action( self._parent, "Undo"          , "Undo"                                   , SK.Undo                      )
        self.editRedo           = Action( self._parent, "Redo"          , "Redo"                                   , SK.Redo                      )
        self.editCancel         = Action( self._parent, "Cancel"        , "Cancel the current action"              , SK.Cancel                    )
        self.editComplete       = Action( self._parent, "Complete"      , "Complete the current action"            , SK.InsertParagraphSeparator  )
        self.editSelectAll      = Action( self._parent, "Select All"    , "Select all"                             , SK.SelectAll                 )
        self.editSelectArea     = Action( self._parent, "Select Area"   , "Select area"                            , None                         )
        self.editDeselectAll    = Action( self._parent, "Deselect All"  , "Deselect all"                           , SK.Deselect                  )
        self.editCut            = Action( self._parent, "Cut"           , "Cut"                                    , SK.Cut                       )
        self.editCopy           = Action( self._parent, "Copy"          , "Copy"                                   , SK.Copy                      )
        self.editPaste          = Action( self._parent, "Paste"         , "Paste"                                  , SK.Paste                     )
        self.editDelete         = Action( self._parent, "Delete"        , "Delete"                                 , SK.Delete                    )
        self.editDuplicate      = Action( self._parent, "Duplicate"     , "Duplicate"                              , "Ctrl+D"                     )
        self.editSlide          = Action( self._parent, "Slide"         , "Slide"                                  , None                         )
        self.editMove           = Action( self._parent, "Move"          , "Move"                                   , None                         )
        self.editResize         = Action( self._parent, "Resize"        , "Resize"                                 , None                         )
        self.editAppearance     = Action( self._parent, "Appearance..." , "Edit appearance of selected element(s)" , None                         )
        self.editQuery          = Action( self._parent, "Query"         , "Query"                                  , "Ctrl+Q"                     )
        self.viewZoomAll        = Action( self._parent, "Zoom All"      , "Zoom to fit all"                        , "Ctrl+Home"                  )
        self.viewZoomSheet      = Action( self._parent, "Zoom Sheet"    , "Zoom to fit sheet"                      , "Ctrl+Shift+S"               )
        self.viewZoomArea       = Action( self._parent, "Zoom Area"     , "Zoom to area"                           , "Ctrl+Shift+W"               )
        self.viewZoomIn         = Action( self._parent, "Zoom In"       , "Zoom in"                                , "Ctrl++"                     )
        self.viewZoomOut        = Action( self._parent, "Zoom Out"      , "Zoom out"                               , "Ctrl+-"                     )
        self.viewPan            = Action( self._parent, "Pan"           , "Pan"                                    , None                         )
        self.viewPanUp          = Action( self._parent, "Pan Up"        , "Pan up"                                 , "Ctrl+Up"                    )
        self.viewPanDown        = Action( self._parent, "Pan Down"      , "Pan down"                               , "Ctrl+Down"                  )
        self.viewPanLeft        = Action( self._parent, "Pan Left"      , "Pan left"                               , "Ctrl+Left"                  )
        self.viewPanRight       = Action( self._parent, "Pan Right"     , "Pan right"                              , "Ctrl+Right"                 )
        self.viewGridDisplay    = Action( self._parent, "Grid Display"  , "Toggle grid display"                    , "Ctrl+G"       , True , True )
        self.viewGridSnap       = Action( self._parent, "Grid Snap"     , "Toggle grid snap"                       , "Ctrl+Shift+G" , True , True )
        self.viewThemeDark      = Action( self._parent, "Dark"          , "Set dark theme"                         , None                         )
        self.viewThemeLightMono = Action( self._parent, "Light Mono"    , "Set light mono theme"                   , None                         )
        self.placePort          = Action( self._parent, "Port"          , "Place Port"                             , "Ctrl+I"                     )
        self.placeBlock         = Action( self._parent, "Block"         , "Place Block"                            , "Ctrl+B"                     )
        self.placeBlockPin      = Action( self._parent, "Block Pin"     , "Place Block Pin"                        , "Ctrl+P"                     )
        self.placeRectangle     = Action( self._parent, "Rectangle"     , "Place Rectangle"                        , "Ctrl+R"                     )
        self.placeTextBlock     = Action( self._parent, "Text Block"    , "Place Text Block"                       , "Ctrl+T"                     )
        self.placeText          = Action( self._parent, "Text"          , "Place Text"                             , "Ctrl+L"                     )
        self.windowExplorer     = Action( self._parent, "Explorer"      , "Show the explorer window"               , None                         )
        self.windowMessages     = Action( self._parent, "Messages"      , "Show the messages window"               , None                         )
        self.windowTranscript   = Action( self._parent, "Transcript"    , "Show the transcript window"             , None                         )
        self.windowLog          = Action( self._parent, "Log"           , "Show the log window"                    , None                         )
        self.windowNext         = Action( self._parent, "Next"          , "Next"                                   , "Ctrl+F6"                    )
        self.windowPrevious     = Action( self._parent, "Previous"      , "Previous"                               , "Ctrl+Shift+F6"              )
        self.helpAbout          = Action( self._parent, "About"         , ""                                       , "Ctrl+Shift+T"               )

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
        self.editCancel      .setEnabled(en)
        self.editComplete    .setEnabled(en)
        self.editDuplicate   .setEnabled(en)
        self.editMove        .setEnabled(en)
        self.editSlide       .setEnabled(en)
        self.editResize      .setEnabled(en)
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
            self.editSlide      .setEnabled( n > 0 )
            self.editMove       .setEnabled( n > 0 )
            self.editResize     .setEnabled( n > 0 )
            self.editAppearance .setEnabled( n > 0 )
        except RuntimeError:
            pass  # Objects deleted during shutdown
        except Exception as e:
            logger.error(f"Exception in onSelectionChanged: {e}")
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
