from typing import Self

from PyQt6.QtWidgets import QApplication, QMdiSubWindow
from PyQt6.QtGui     import QKeySequence

from ...app import window

from ...core.defs import MIME_TYPE

from ...widgets.graphics.views.drawing  import DrawingSubWindow
from ...widgets.graphics.scenes.drawing import DrawingScene

from ..private  import Action


class Actions:
    _scene  : DrawingScene | None

    def __init__(self : Self) -> None:
        self._scene  = None
        SK = QKeySequence.StandardKey

        self.fileNewDesign      = Action( window(), "Design"        , "Create a new design"                    , "Ctrl+N"                     )  # noqa E501
        self.fileNewLibrary     = Action( window(), "Library"       , "Create a new library"                   , None                         )  # noqa E501
        self.fileOpen           = Action( window(), "Open"          , "Open database"                          , "Ctrl+O"                     )  # noqa E501
        self.fileSave           = Action( window(), "Save"          , "Save database"                          , "Ctrl+S"                     )  # noqa E501
        self.fileSaveAs         = Action( window(), "Save As"       , "Save database as"                       , None                         )  # noqa E501
        self.fileOpenMRU1       = Action( window(), "&1:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU2       = Action( window(), "&2:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU3       = Action( window(), "&3:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU4       = Action( window(), "&4:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU5       = Action( window(), "&5:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU6       = Action( window(), "&6:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU7       = Action( window(), "&7:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU8       = Action( window(), "&8:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileOpenMRU9       = Action( window(), "&9:"           , "Open recent file"                       , None                         )  # noqa E501
        self.fileExit           = Action( window(), "Exit"          , "Exit the application"                   , SK.Quit                      )  # noqa E501
        self.editCancel         = Action( window(), "Cancel"        , "Cancel current operation"               , SK.Cancel                    )  # noqa E501
        self.editUndo           = Action( window(), "Undo"          , "Undo"                                   , SK.Undo                      )  # noqa E501
        self.editRedo           = Action( window(), "Redo"          , "Redo"                                   , SK.Redo                      )  # noqa E501
        self.editCut            = Action( window(), "Cut"           , "Cut"                                    , SK.Cut                       )  # noqa E501
        self.editCopy           = Action( window(), "Copy"          , "Copy"                                   , SK.Copy                      )  # noqa E501
        self.editPaste          = Action( window(), "Paste"         , "Paste"                                  , SK.Paste                     )  # noqa E501
        self.editDelete         = Action( window(), "Delete"        , "Delete"                                 , SK.Delete                    )  # noqa E501
        self.editDuplicate      = Action( window(), "Duplicate"     , "Duplicate"                              , "Ctrl+D"                     )  # noqa E501
        self.editSelectArea     = Action( window(), "Select Area"   , "Select area"                            , None                         )  # noqa E501
        self.editSelectAll      = Action( window(), "Select All"    , "Select all"                             , SK.SelectAll                 )  # noqa E501
        self.editProperties     = Action( window(), "Properties..." , "Edit properties of selected element(s)" , None                         )  # noqa E501
        self.editAppearance     = Action( window(), "Appearance..." , "Edit appearance of selected element(s)" , None                         )  # noqa E501
        self.editQuery          = Action( window(), "Query"         , "Query"                                  , "Ctrl+Q"                     )  # noqa E501
        self.viewZoomAll        = Action( window(), "Zoom All"      , "Zoom to fit all"                        , "Ctrl+Home"                  )  # noqa E501
        self.viewZoomSheet      = Action( window(), "Zoom Sheet"    , "Zoom to fit sheet"                      , "Ctrl+Shift+S"               )  # noqa E501
        self.viewZoomArea       = Action( window(), "Zoom Area"     , "Zoom to area"                           , "Ctrl+Shift+W"               )  # noqa E501
        self.viewZoomIn         = Action( window(), "Zoom In"       , "Zoom in"                                , "Ctrl++"                     )  # noqa E501
        self.viewZoomOut        = Action( window(), "Zoom Out"      , "Zoom out"                               , "Ctrl+-"                     )  # noqa E501
        self.viewPan            = Action( window(), "Pan"           , "Pan"                                    , None                         )  # noqa E501
        self.viewPanUp          = Action( window(), "Pan Up"        , "Pan up"                                 , "Ctrl+Up"                    )  # noqa E501
        self.viewPanDown        = Action( window(), "Pan Down"      , "Pan down"                               , "Ctrl+Down"                  )  # noqa E501
        self.viewPanLeft        = Action( window(), "Pan Left"      , "Pan left"                               , "Ctrl+Left"                  )  # noqa E501
        self.viewPanRight       = Action( window(), "Pan Right"     , "Pan right"                              , "Ctrl+Right"                 )  # noqa E501
        self.viewGridDisplay    = Action( window(), "Grid Display"  , "Toggle grid display"                    , "Ctrl+G"       , True , True )  # noqa E501
        self.viewGridSnap       = Action( window(), "Grid Snap"     , "Toggle grid snap"                       , "Ctrl+Shift+G" , True , True )  # noqa E501
        self.viewThemeDark      = Action( window(), "Dark"          , "Set dark theme"                         , None                         )  # noqa E501
        self.viewThemeLightMono = Action( window(), "Light Mono"    , "Set light mono theme"                   , None                         )  # noqa E501
        self.placePort          = Action( window(), "Port"          , "Place Port"                             , "Ctrl+I"                     )  # noqa E501
        self.placeBlock         = Action( window(), "Block"         , "Place Block"                            , "Ctrl+B"                     )  # noqa E501
        self.placeBlockPin      = Action( window(), "Block Pin"     , "Place Block Pin"                        , "Ctrl+P"                     )  # noqa E501
        self.placeConnection    = Action( window(), "Connection"    , "Place Connection"                       , "C"                          )  # noqa E501
        self.placeLine          = Action( window(), "Line"          , "Place Line"                             , "Ctrl+L"                     )  # noqa E501
        self.placeRectangle     = Action( window(), "Rectangle"     , "Place Rectangle"                        , "Ctrl+R"                     )  # noqa E501
        self.placeText          = Action( window(), "Text"          , "Place Text"                             , "Ctrl+T"                     )  # noqa E501
        self.placeTextBlock     = Action( window(), "Text Block"    , "Place Text Block"                       , "Ctrl+K"                     )  # noqa E501
        self.windowExplorer     = Action( window(), "Explorer"      , "Show the explorer window"               , None                         )  # noqa E501
        self.windowMessages     = Action( window(), "Messages"      , "Show the messages window"               , None                         )  # noqa E501
        self.windowTranscript   = Action( window(), "Transcript"    , "Show the transcript window"             , None                         )  # noqa E501
        self.windowLog          = Action( window(), "Log"           , "Show the log window"                    , None                         )  # noqa E501
        self.windowNext         = Action( window(), "Next"          , "Next"                                   , "Ctrl+F6"                    )  # noqa E501
        self.windowPrevious     = Action( window(), "Previous"      , "Previous"                               , "Ctrl+Shift+F6"              )  # noqa E501
        self.helpAbout          = Action( window(), "About"         , ""                                       , "Ctrl+Shift+T"               )  # noqa E501

        self.onSubWindowActivated(None)

    def actionEnable(self : Self, name : str, enable : bool) -> None:
        getattr(self, name).setEnabled(enable)

    def onSubWindowActivated(
        self      : Self,
        subwindow : QMdiSubWindow | None
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

    def onClipboardDataChanged(self : Self) -> None:
        if not self._scene:
            en = False
        else:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            en = mime_data is not None and mime_data.hasFormat(MIME_TYPE)
        self.editPaste.setEnabled(en)

    def onCanUndoChanged(self : Self, canUndo : bool) -> None:
        self.editUndo.setEnabled(canUndo)

    def onCanRedoChanged(self : Self, canRedo : bool) -> None:
        self.editRedo.setEnabled(canRedo)

# TODO control status of edit cancel/complete
