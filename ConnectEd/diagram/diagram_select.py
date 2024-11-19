class DiagramSelectMixin:
    class SelectFilter:
        class Functional:
            def __init__(self):
                self.title     = True
                self.block     = True
                self.pin       = True
                self.wire      = True
                self.tap       = True
                self.junction  = True
                self.port      = True
                self.code      = True
        class Decorative:
            def __init__(self):
                self.line      = True
                self.rectangle = True
                self.polygon   = True
                self.arc       = True
                self.ellipse   = True
                self.textline  = True
                self.textbox   = True
                self.image     = True
        def __init__(self):
            self.functional = self.Functional()
            self.decorative = self.Decorative()

    def selectPoint(self, p):
        for item in self.content:
            if item.select(p):
                return True
        return False
