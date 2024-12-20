ORG_NAME = 'ConnectEd'
APP_NAME = 'ConnectEd'
APP_EXT = 'ced'        # extension for ConnectEd files

class Counter:
    def __init__(self):
        self.count = 1

    def __str__(self):
        self.count += 1
        return str(self.count)

new_diagram_number = Counter()
