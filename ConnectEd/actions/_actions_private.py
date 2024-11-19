from inspect import stack
from PyQt6.QtWidgets import QMessageBox

def _actions_todo:
    caller_frame = stack()[1]
    caller_function_name = caller_frame[function]
    caller_parent = caller_frame[f_locals][self].parent
    QMessageBox.about(caller_parent, "TODO", caller_function_name)