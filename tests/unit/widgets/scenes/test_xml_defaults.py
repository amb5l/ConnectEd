"""File XML publishes defaults; the clipboard does not."""

import logging

import pytest
from PyQt6.QtCore import (
    QBuffer, QByteArray, QIODevice, QPointF,
    QXmlStreamReader, QXmlStreamWriter,
)
from PyQt6.QtWidgets import QApplication

from ConnectEd.app                             import ConnectEdApp
from ConnectEd.core.settings                   import Settings
from ConnectEd.widgets.graphics.items.port     import PortItem
from ConnectEd.widgets.graphics.items.text     import TextItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


def _scene_xml(scene : DiagramScene) -> str:
    buffer = QBuffer()
    assert buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    writer = QXmlStreamWriter(buffer)
    writer.setAutoFormatting(True)
    writer.writeStartDocument()
    scene.toXml(writer)
    writer.writeEndDocument()
    buffer.close()
    return buffer.data().data().decode("utf-8")


def _item_xml(item : PortItem) -> str:
    buffer = QBuffer()
    assert buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    writer = QXmlStreamWriter(buffer)
    writer.writeStartDocument()
    item.toXml(writer)
    writer.writeEndDocument()
    buffer.close()
    return buffer.data().data().decode("utf-8")


def _load_scene(xml : str) -> DiagramScene:
    buffer = QBuffer()
    buffer.setData(QByteArray(xml.encode("utf-8")))
    assert buffer.open(QIODevice.OpenModeFlag.ReadOnly)
    reader = QXmlStreamReader(buffer)
    while not reader.atEnd():
        reader.readNext()
        if reader.isStartElement() and reader.name() == "HdlSchematicDiagram":
            return DiagramScene.fromXml(reader)
    raise AssertionError(reader.errorString())


def _elements(xml : str) -> list[tuple[str, str, dict[str, str]]]:
    reader = QXmlStreamReader(xml)
    stack  : list[str] = []
    found  : list[tuple[str, str, dict[str, str]]] = []
    while not reader.atEnd():
        reader.readNext()
        if reader.isStartElement():
            parent = stack[-1] if stack else ""
            attrs  = {
                str(attr.name()) : str(attr.value())
                for attr in reader.attributes()
            }
            found.append((parent, str(reader.name()), attrs))
            if not reader.isEndElement():
                stack.append(str(reader.name()))
        elif reader.isEndElement() and stack:
            stack.pop()
    return found


def test_file_publishes_defaults_and_round_trips(
    connect_ed_app : ConnectEdApp,
) -> None:
    del connect_ed_app
    scene = DiagramScene()
    origin = PortItem()
    origin.setName("A")
    origin.setPos(QPointF(0, 0))
    scene.addItem(origin)
    turned = PortItem()
    turned.setName("B")
    turned.setPos(QPointF(40, 50))
    turned.setRotation(180)
    scene.addItem(turned)
    narrow = TextItem()
    narrow.setText("narrow")
    narrow.setPos(QPointF(1, 1))
    narrow.setWidth(-1)
    scene.addItem(narrow)
    wide = TextItem()
    wide.setText("wide")
    wide.setPos(QPointF(2, 2))
    wide.setWidth(-2)
    scene.addItem(wide)

    xml      = _scene_xml(scene)
    elements = _elements(xml)
    port_defaults = [
        attrs for parent, tag, attrs in elements
        if parent == "Defaults" and tag == "Port"
    ]
    assert len(port_defaults) == 1
    defaults = port_defaults[0]
    assert "Name"     not in defaults
    assert "Dir"      not in defaults
    assert "X"        not in defaults
    assert "Y"        not in defaults
    assert defaults["Rotation"] == "0"
    assert defaults["Comment"]  == ""
    assert defaults["MirrorH"]  == "False"
    assert defaults["MirrorV"]  == "False"
    text_defaults = [
        attrs for parent, tag, attrs in elements
        if parent == "Defaults" and tag == "Text"
    ]
    assert len(text_defaults) == 1
    assert "Width" not in text_defaults[0]
    texts = {
        attrs["Text"] : attrs
        for parent, tag, attrs in elements
        if parent == "HdlSchematicDiagram" and tag == "Text"
    }
    assert texts["narrow"]["Width"] == "-1"
    assert texts["wide"]["Width"] == "-2"

    body = {
        attrs["Name"] : attrs
        for parent, tag, attrs in elements
        if parent == "HdlSchematicDiagram" and tag == "Port"
    }
    assert body["A"]["X"] == "0"
    assert body["A"]["Y"] == "0"
    assert "Rotation" not in body["A"]
    assert body["B"]["Rotation"] == "180"
    assert body["B"]["X"] == "40"
    assert body["B"]["Y"] == "50"

    loaded = _load_scene(xml)
    ports  = {
        item.name() : item
        for item in loaded.items()
        if isinstance(item, PortItem)
    }
    assert ports["A"].pos() == QPointF(0, 0)
    assert ports["A"].rotation() == 0
    assert ports["B"].pos() == QPointF(40, 50)
    assert ports["B"].rotation() == 180


def test_clipboard_item_keeps_worthy_omission(
    connect_ed_app : ConnectEdApp,
) -> None:
    del connect_ed_app
    port = PortItem()
    port.setName("A")
    port.setPos(QPointF(0, 0))
    elements = _elements(_item_xml(port))
    assert all(tag != "Defaults" for _parent, tag, _attrs in elements)
    attrs = next(attrs for _parent, tag, attrs in elements if tag == "Port")
    assert "X"        not in attrs
    assert "Y"        not in attrs
    assert "Rotation" not in attrs
    assert attrs["Name"] == "A"
    assert attrs["Dir"]  == "in"


def test_load_without_defaults_keeps_constructor_omission(
    connect_ed_app : ConnectEdApp,
    caplog,
) -> None:
    del connect_ed_app
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<ConnectEd>
  <HdlSchematicDiagram Name="sheet" Sheet_Name="A4 (landscape)" Sheet_Width="1169" Sheet_Height="827" Margin="10" Border="1">
    <Port Name="clk" Dir="in" X="10" Y="20" Rotation="180"/>
  </HdlSchematicDiagram>
</ConnectEd>
"""
    with caplog.at_level(logging.WARNING, logger="test"):
        loaded = _load_scene(xml)
    assert not any("no default" in rec.message for rec in caplog.records)
    ports = [item for item in loaded.items() if isinstance(item, PortItem)]
    assert len(ports) == 1
    assert ports[0].name() == "clk"
    assert ports[0].rotation() == 180
    assert ports[0].pos() == QPointF(10, 20)


def test_load_honors_file_default_and_warns(
    connect_ed_app : ConnectEdApp,
    caplog,
) -> None:
    del connect_ed_app
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<ConnectEd>
  <HdlSchematicDiagram Name="sheet" Sheet_Name="A4 (landscape)" Sheet_Width="1169" Sheet_Height="827" Margin="10" Border="1">
    <Defaults>
      <Port Rotation="90" Comment=""/>
    </Defaults>
    <Port Name="clk" Dir="in" X="10" Y="20"/>
  </HdlSchematicDiagram>
</ConnectEd>
"""
    with caplog.at_level(logging.WARNING, logger="test"):
        loaded = _load_scene(xml)
    ports = [item for item in loaded.items() if isinstance(item, PortItem)]
    assert len(ports) == 1
    assert ports[0].rotation() == 90
    assert any(
        "disagrees" in rec.message and "Rotation" in rec.message
        for rec in caplog.records
    )


def test_load_warns_when_required_attribute_is_absent(
    connect_ed_app : ConnectEdApp,
    caplog,
) -> None:
    del connect_ed_app
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<ConnectEd>
  <HdlSchematicDiagram Name="sheet" Sheet_Name="A4 (landscape)" Sheet_Width="1169" Sheet_Height="827" Margin="10" Border="1">
    <Defaults>
      <Port Rotation="0"/>
    </Defaults>
    <Port Dir="in" X="10" Y="20"/>
  </HdlSchematicDiagram>
</ConnectEd>
"""
    with caplog.at_level(logging.WARNING, logger="test"):
        loaded = _load_scene(xml)
    assert any(
        "omits Name" in rec.message for rec in caplog.records
    )
    ports = [item for item in loaded.items() if isinstance(item, PortItem)]
    assert len(ports) == 1
    assert ports[0].name() == ""
