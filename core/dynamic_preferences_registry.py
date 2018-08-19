from dynamic_preferences.types import BooleanPreference, StringPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

general = Section('general')
witness = Section('witness')


@global_preferences_registry.register
class Released(BooleanPreference):
    section = general
    name = 'released'
    default = False

@global_preferences_registry.register
class OurWitnessName(StringPreference):
    section = witness
    name = 'our_witness_name'
    default = 'noisy.witness'

@global_preferences_registry.register
class AskingForVotes(BooleanPreference):
    section = witness
    name = 'asking_for_votes'
    default = False
