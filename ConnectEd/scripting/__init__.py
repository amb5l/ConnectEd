import sys



from collections.abc import Callable



# app

from ..app import ConnectEdApp as App, app



# ConnectEd types — main window

from ..widgets.window import Window



# ConnectEd types — chrome

from ..widgets.window.menu_bar import MenuBar

from ..widgets.window.status_bar import StatusBar

from ..widgets.window.mdi_area import MdiArea



# ConnectEd types — docks

from ..widgets.window.navigator import NavigatorDock

from ..widgets.window.messages_view import MessagesViewDock

from ..widgets.window.transcript_view import TranscriptViewDock

from ..widgets.window.log_view import LogViewDock

from ..widgets.window.ai_chat import AiChatDock

from ..widgets.window.netlist import NetlistBrowserDock



# ConnectEd types — menus

from ..widgets.menu import Menu

from ..widgets.action import Action



# scripting

from .qt import GuiDriver, QtScripting

from .gui import Gui, gui





def run(

    func : Callable[[App], None],

    argv : list[str] = []

) -> None:

    try:

        if App.instance() is None:

            sys.argv = [sys.argv[0]] + argv + sys.argv[1:]

            from ..main import main

            main(func)

        else:

            func(app())

    except Exception as e:
        print(f"Script error: {e}")
        import traceback
        traceback.print_exc()
        raise





__all__ = [

    # scripting

    "run",

    "GuiDriver",

    "QtScripting",

    "Gui",

    "gui",

    # ConnectEd types - application

    "App",

    # ConnectEd types — main window

    "Window",

    # ConnectEd types — chrome

    "MenuBar",

    "StatusBar",

    "MdiArea",

    # ConnectEd types — docks

    "NavigatorDock",

    "MessagesViewDock",

    "TranscriptViewDock",

    "LogViewDock",

    "AiChatDock",

    "NetlistBrowserDock",

    # ConnectEd types — menus

    "Menu",

    "Action",

]

