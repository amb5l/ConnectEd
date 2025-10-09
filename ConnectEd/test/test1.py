from ConnectEd import api as ce

ce.initCli()
design_db = ce.DesignDbNode()
print("design database path =", design_db.getPath())
diagrams = design_db.diagrams()
if len(diagrams) != 1:
    raise Exception("expected 1 diagram, got", len(diagrams))
diagram = diagrams[0]
print("diagram name =", diagram.getName())
scene = diagram.getScene()
print("  scene size =", scene.getSize())
scene.placeRectangle(100, 100, 100, 100)
scene.placeTextBlock("Hello, World!", 300, 300)
design_db.save("test1.xml")
