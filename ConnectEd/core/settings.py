from types import SimpleNamespace
# Use Pydantic v1 compatibility mode
from pydantic.v1 import BaseModel

from PyQt6.QtCore import QSettings, QSize, QSizeF, Qt
from PyQt6.QtGui  import QColor

from .logger import logger
from .defs   import ORG_NAME, APP_NAME
from .utils  import get_default_path

class SettingsModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

class Theme(SettingsModel):
    background : QColor
    grid       : QColor

class Settings(SettingsModel):
    ################################################################################

    class Startup(SettingsModel):
        geometry : bytes | None = None
    startup : Startup = Startup()

    class Themes(SettingsModel):
        class Dark(Theme):
            background : QColor = QColor(0, 0, 0)
            grid : QColor = QColor(32, 32, 32)
        dark : Dark = Dark()
        class Light(Theme):
            background : QColor = QColor(128, 128, 128)
            grid : QColor = QColor(32, 32, 32)
        light : Light = Light()
    themes : Themes = Themes()

    class Prefs(SettingsModel):
        class File(SettingsModel):
            class New(SettingsModel):
                sheet  : str = 'A4'
                margin : int = 10
            new : New = New()
            class Open(SettingsModel):
                dir : str = get_default_path()
            open : Open = Open()
            class Save(SettingsModel):
                dir : str = get_default_path()
            save : Save = Save()
        file : File = File()
        class View(SettingsModel):
            theme : str = 'dark'
            class Grid(SettingsModel):
                display : bool = True
                snap    : bool = True
                x       : int = 10
                y       : int = 10
            grid : Grid = Grid()
            overscan : int = 3 # TODO: change to 0
        view : View = View()
        class Debug(SettingsModel):
            overscan : bool = True
            canvas   : bool = True
        debug : Debug = Debug()
    prefs : Prefs = Prefs()

    @property
    def theme(self) -> Theme:
        theme_name = self.prefs.view.theme
        valid_themes = [name for name in dir(self.themes)
                       if not name.startswith('_') and isinstance(getattr(self.themes, name), Theme)]
        if theme_name in valid_themes:
            return getattr(self.themes, theme_name)
        self.prefs.view.theme = 'dark'
        return self.themes.dark

    ################################################################################

    def __init__(self : 'Settings'):
        super().__init__()

    def reset(self : 'Settings'):
        logger.debug('clearing all settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()

    def load(self : 'Settings'):
        """Load settings from QSettings storage into this Pydantic model."""
        logger.debug('loading settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in dir(self):
            if attr_name.startswith('_') or callable(getattr(self, attr_name)):
                continue
            attr = getattr(self, attr_name)
            if hasattr(attr, '__fields__'): # is a Pydantic model
                logger.debug(f'Loading settings for {attr_name}')
                qsettings.beginGroup(attr_name)
                self._load_model(qsettings, attr)
                qsettings.endGroup()

    def save(self : 'Settings'):
        """Save settings from this Pydantic model to QSettings storage."""
        logger.debug('saving settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in dir(self):
            if attr_name.startswith('_') or callable(getattr(self, attr_name)):
                continue
            attr = getattr(self, attr_name)
            if hasattr(attr, '__fields__'): # is a Pydantic model
                logger.debug(f'Saving settings for {attr_name}')
                qsettings.beginGroup(attr_name)
                self._save_model(qsettings, attr)
                qsettings.endGroup()

    def _load_model(
        self      : 'Settings',
        qsettings : QSettings,
        model     : SettingsModel
    ):
        """
        Load settings from QSettings into a Pydantic model.

        Args:
            qsettings: The QSettings object positioned at the current group
            model: The Pydantic model to load settings into
        """
        # Load direct values
        for key in qsettings.childKeys():
            value = qsettings.value(key)
            if value is not None:
                logger.debug(f'loading setting: {qsettings.group()}/{key} = {value}')
                try:
                    # Convert the string value to the appropriate type
                    converted_value = self._text_to_value(value)
                    # Set the attribute on the model
                    setattr(model, key, converted_value)
                except (ValueError, AttributeError) as e:
                    logger.warning(f'Error loading setting {key}: {e}')

        # Load nested groups (submodels)
        for group in qsettings.childGroups():
            # Check if this group corresponds to a field in the model
            if hasattr(model, group):
                submodel = getattr(model, group)
                # Check if it's a model by checking if it has __fields__
                if hasattr(submodel, '__fields__'):
                    qsettings.beginGroup(group)
                    self._load_model(qsettings, submodel)
                    qsettings.endGroup()

    def _save_model(
        self      : 'Settings',
        qsettings : QSettings,
        model     : SettingsModel
    ):
        """
        Save settings from a Pydantic model to QSettings.

        Args:
            qsettings: The QSettings object positioned at the current group
            model: The Pydantic model to save settings from
        """
        # Get all fields from the model
        model_dict = model.dict()

        for key, value in model_dict.items():
            if isinstance(value, dict):
                # This is likely a nested model
                if hasattr(model, key) and hasattr(getattr(model, key), '__fields__'):
                    qsettings.beginGroup(key)
                    self._save_model(qsettings, getattr(model, key))
                    qsettings.endGroup()
            else:
                # This is a direct value
                logger.debug(f'saving setting: {qsettings.group()}/{key} = {value}')
                qsettings.setValue(key, self._value_to_text(value))

    def _text_to_value(self, text_value):
        """Convert a text value from QSettings to the appropriate Python type."""
        if not isinstance(text_value, str):
            return text_value
        try:
            typeName, valueStr = text_value.split(':', 1)
        except ValueError:
            # If there's no type prefix, return as is
            return text_value
        match typeName:
            case 'NoneType'   : return None
            case 'bytes'      : return bytes.fromhex(valueStr)
            case 'str'        : return valueStr
            case 'int'        : return int(valueStr)
            case 'float'      : return float(valueStr)
            case 'bool'       : return valueStr == 'True'
            case 'QSize'      : return QSize(*map(int, valueStr[1:-1].split(',')))
            case 'QSizeF'     : return QSizeF(*map(float, valueStr[1:-1].split(',')))
            case 'QColor'     : return QColor.fromRgba(int(valueStr,0))
            case 'PenStyle'   : return Qt.PenStyle[valueStr]
            case 'BrushStyle' : return Qt.BrushStyle[valueStr]
            case _:
                raise ValueError(f'Unsupported type: {typeName}')

    def _value_to_text(self, value):
        """Convert a Python value to a text representation for QSettings."""
        typeName = type(value).__name__
        match typeName:
            case 'NoneType'   : valueStr = 'None'
            case 'bytes'      : valueStr = value.hex()
            case 'str'        : valueStr = value
            case 'int'        : valueStr = str(value)
            case 'float'      : valueStr = str(value)
            case 'bool'       : valueStr = str(value)
            case 'QSize'      : valueStr = f'({value.width()},{value.height()})'
            case 'QSizeF'     : valueStr = f'({value.width()},{value.height()})'
            case 'QColor'     : valueStr = hex(value.rgba())
            case 'PenStyle'   : valueStr = str(value).replace('PenStyle.', '')
            case 'BrushStyle' : valueStr = str(value).replace('BrushStyle.', '')
            case _ :
                raise ValueError(f'Unsupported type: {typeName}')
        return typeName + ':' + valueStr

    def dump(self : 'Settings') -> str:
        """
        Dump all settings as a formatted string for debugging or display.

        Returns:
            A formatted string representation of all settings
        """
        lines = ["Settings:"]
        self._dump_model(lines, self, indent=2)
        return "\n".join(lines)

    def _dump_model(self, lines: list, model: SettingsModel, indent: int = 0, prefix: str = ""):
        """
        Helper method to recursively dump a model and its nested models.

        Args:
            lines: List to append formatted lines to
            model: The model to dump
            indent: Current indentation level
            prefix: Prefix for the current model (for nested models)
        """
        # Get all fields from the model
        model_dict = model.dict()

        for key, value in model_dict.items():
            # Skip private attributes
            if key.startswith('_'):
                continue

            # Format the current line
            current_prefix = f"{prefix}." if prefix else ""
            current_key = f"{current_prefix}{key}"

            if isinstance(value, dict):
                # This is likely a nested model
                if hasattr(model, key) and hasattr(getattr(model, key), '__fields__'):
                    # Add a header for the nested model
                    lines.append(f"{' ' * indent}{current_key}:")
                    # Recursively dump the nested model
                    self._dump_model(
                        lines,
                        getattr(model, key),
                        indent + 2,
                        current_key
                    )
            else:
                # This is a direct value - format it nicely
                type_name = type(value).__name__
                if isinstance(value, QColor):
                    # Special formatting for QColor
                    value_str = f"RGB({value.red()}, {value.green()}, {value.blue()})"
                elif isinstance(value, (QSize, QSizeF)):
                    # Special formatting for QSize/QSizeF
                    value_str = f"({value.width()}, {value.height()})"
                else:
                    # Default formatting
                    value_str = str(value)

                lines.append(f"{' ' * indent}{current_key} = {value_str} ({type_name})")
