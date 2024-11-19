class CanvasSelectionMixin:
    def selectionClear(self):
        self.selection = []
        self.parent().statusBar.select.setText('No items selected')
        # disable selection-dependent actions
        self._actionEnable('Edit', 'editCut'              , False)
        self._actionEnable('Edit', 'editCopy'             , False)
        self._actionEnable('Edit', 'editDelete'           , False)
        self._actionEnable('Edit', 'editMirrorHorizontal' , False)
        self._actionEnable('Edit', 'editMirrorVertical'   , False)
        self._actionEnable('Edit', 'editRotate'           , False)
        self._actionEnable('Edit', 'editLock'             , False)
        self._actionEnable('Edit', 'editUnlock'           , False)
        self._actionEnable('Edit', 'editProperties'       , False)

    def selectionAdd(self, item):
        self.selection.append(item)
        l = len(self.selection)
        s = 's' if l > 1 else ''
        self.parent().statusBar.select.setText(f'{l} item{s} selected')
        # enable selection-dependent actions
        self._actionEnable('Edit', 'editCut'              , True)
        self._actionEnable('Edit', 'editCopy'             , True)
        self._actionEnable('Edit', 'editDelete'           , True)
        self._actionEnable('Edit', 'editMirrorHorizontal' , True)
        self._actionEnable('Edit', 'editMirrorVertical'   , True)
        self._actionEnable('Edit', 'editRotate'           , True)
        self._actionEnable('Edit', 'editLock'             , True)
        self._actionEnable('Edit', 'editUnlock'           , True)
        self._actionEnable('Edit', 'editProperties'       , True)
