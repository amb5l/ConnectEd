__all__ = [
    'count',
    'check',
    'connect_actions_to_slots',
    'get_default_path'
]

import os
import platform

from typing import Any


class Counter:
    count : int

    def __init__(self):
        self.count = 1

    def __str__(self):
        r = str(self.count)
        self.count += 1
        return r

count = Counter()

def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b

def connect_actions_to_slots(actions : Any, slots : Any) -> None:
    action_names = [a for a in dir(actions) if not a.startswith('_') and not callable(getattr(actions, a))]
    slot_names   = [s for s in dir(slots)   if not s.startswith('_')]
    error = False
    error &= check(len(action_names) > 0, 'No actions found')
    error &= check(len(slot_names)   > 0, 'No slots found')
    error &= check(len(action_names) == len(slot_names), \
        f'Number of actions ({len(action_names)}) and slots ({len(slot_names)}) do not match')
    for action_name in action_names:
        error &= check(action_name in slot_names, \
            f'No matching slot found for action "{action_name}"')
    for slot_name in slot_names:
        error &= check(slot_name in action_names, \
            f'No matching action found for slot "{slot_name}"')
    if error:
        raise Exception('Action-slot mismatch')
    for action_name in action_names:
        action = getattr(actions, action_name)
        slot = getattr(slots, action_name)
        action.triggered.connect(slot)

def get_default_path() -> str:
    if platform.system() == 'Windows':
        if 'WORK' in os.environ:
            r = os.environ['WORK']
        elif 'USERPROFILE' in os.environ:
            r = os.environ['USERPROFILE']
        elif 'HOMEPATH' in os.environ:
            r = os.environ['HOMEPATH']
        elif 'HOMEDRIVE' in os.environ:
            r = os.environ['HOMEDRIVE']
        else:
            r = 'C:/'
    else:
        if 'WORK' in os.environ:
            r = os.environ['WORK']
        else:
            r = '~'
    return r

