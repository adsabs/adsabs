
"""
Configuration for all the blueprints that should be registered in the system
each tuple contains 
1: the module where the blueprint is
2: blueprint name (note, the blueprints must be defined or imported in the __init__.py of each module
3: prefix for the application
"""

#blueprints from core module
from adsabs.core import index

_BLUEPRINTS_CORE = [
    {'module':index, 'blueprint':'index_blueprint', 'prefix':''},
]

#blueprints from all other modules
from adsabs.modules import search, user, api, abs

_BLUEPRINTS_MODULES = [
    {'module':user, 'blueprint':'user_blueprint', 'prefix':'/user'},
    {'module':search, 'blueprint':'search_blueprint', 'prefix':'/search'},
    {'module':api, 'blueprint':'api_blueprint', 'prefix':'/api'},
    {'module':abs, 'blueprint':'abs_blueprint', 'prefix':'/abs' }
]

BLUEPRINTS = _BLUEPRINTS_CORE + _BLUEPRINTS_MODULES