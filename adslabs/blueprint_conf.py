
"""
Configuration for all the blueprints that should be registered in the system
each tuple contains 
1: the module where the blueprint is
2: blueprint name (note, the blueprints must be defined in the __init__.py of each module
3: prefix for the application
"""

#blueprints from core module
from adslabs.core import index, auth

_BLUEPRINTS_CORE = [
    (index, 'index_blueprint', '/'),
    (auth, 'auth_blueprint', '/auth'),
    
]

#blueprints from all other modules
from adslabs.modules import search

_BLUEPRINTS_MODULES = [
    (search, 'search_blueprint', '/search'),
    
]

BLUEPRINTS = _BLUEPRINTS_CORE + _BLUEPRINTS_MODULES