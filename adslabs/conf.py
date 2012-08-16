
"""
Configuration for all the bleprints that should be registered in the system
each tuple contains 
1: namespace for the module name
2: blueprint name (note, the blueprints should be defined in the __init__.py of each module
3: prefix for the application
"""

_BLUEPRINTS_CORE = [
    ('core.auth', 'auth_blueprint', 'auth'),
    
]

_BLUEPRINTS_MODULES = [
    ('modules.search', 'search_blueprint', 'search'),
    
]

BLUEPRINTS = _BLUEPRINTS_CORE + _BLUEPRINTS_MODULES