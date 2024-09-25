class DiagramSelectMixin:
    def selectPoint(self, p):
        for item in self.content:
            if item.select(p):
                return True
        return False
