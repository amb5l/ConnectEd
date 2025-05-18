from ConnectEd import api as ce

ce.initCli()
diagram = ce.Diagram("MyDiagram", "A4")
diagram.placeRectangle(100, 100, 100, 100)
diagram.placeTextBlock("Hello, World!", 300, 300)
diagram.save("test1.xml")
print("diagram =", diagram)
