from dynamic_preferences.types import BooleanPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

general = Section('general')

@global_preferences_registry.register
class Released(BooleanPreference):
    section = general
    name = 'released'
    default = False
