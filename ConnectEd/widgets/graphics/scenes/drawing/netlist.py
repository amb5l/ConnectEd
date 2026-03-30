from typing      import Self
from collections import defaultdict

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader

from .....core.types import DataKind, Counter
from .....core.xml   import toXmlAttrs
from .....core.utils import underscore2space

from ...properties import PropertiesMixin, InherentProperty


class Net(PropertiesMixin):
    # class attributes
    _PROPERTIES = {
        "ID" : InherentProperty(
            kind   = DataKind.INT,
            getter = lambda self: self._id,
            setter = lambda self, value: setattr(self, "_id", value)
        ),
        "Name" : InherentProperty(
            kind   = DataKind.STR,
            worthy = lambda self: self._name != "",
            getter = lambda self: self._name,
            setter = lambda self, value: setattr(self, "_name", value)
        )
    }

    # instance attributes
    _id    : int | None
    _name  : str | None
    _edges : dict[int, set[int]]  # node ID : list of neighbour node IDs

    def __init__(
        self : Self,
        id   : int | None = None,
        name : str | None = None
    ) -> None:
        self._id = id
        self._name = "" if name is None else name
        self._edges = defaultdict(set)
        self.initProperties()

    def toXml(self, xw : QXmlStreamWriter) -> None:
        # start
        xw.writeStartElement("Net")
        # properties
        toXmlAttrs(self, xw)
        # edges
        pairs = []
        for v1, neighbours in self._edges.items():
            for v2 in neighbours:
                if v1 < v2:
                    pairs.append(f"{v1},{v2}")
        if pairs:
            xw.writeAttribute("Edges", " ".join(pairs))
        # end
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "Net" = cls()
        xml_attrs = xr.attributes()
        for xml_attr in xml_attrs:
            if xml_attr.name() == "Edges":
                pairs = xml_attr.value().split(" ")
                for pair in pairs:
                    s1, s2 = pair.split(",")
                    v1, v2 = int(s1), int(s2)
                    instance._edges[v1].add(v2)
                    instance._edges[v2].add(v1)
            else:
                instance.properties.init(
                    underscore2space(xml_attr.name()), xml_attr.value()
                )
        xr.readNext()
        return instance


class DrawingSceneNetlistMixin:
    _id_net : Counter
    _id_vtx : Counter
    _nets   : dict[int, Net]

    def initNetlist(self : Self) -> None:
        self._id_net = Counter()
        self._id_vtx = Counter()
        self._nets = {}

    def addNet(self : Self, net : Net) -> None:
        self._nets[net._id] = net
