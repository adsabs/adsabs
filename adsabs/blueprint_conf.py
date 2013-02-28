
"""
Configuration for all the blueprints that should be registered in the system
each tuple contains 
1: the module where the blueprint is
2: blueprint name (note, the blueprints must be defined or imported in the __init__.py of each module
3: prefix for the application
"""

#blueprints from core module


_BLUEPRINTS_CORE = [
    
]

#blueprints from all other modules
from adsabs.modules import search, user, api, abs, index, dynamicjs

_BLUEPRINTS_MODULES = [
    {'module':index, 'blueprint':'index_blueprint', 'prefix':''},
    {'module':user, 'blueprint':'user_blueprint', 'prefix':'/user'},
    {'module':search, 'blueprint':'search_blueprint', 'prefix':'/search'},
    {'module':api, 'blueprint':'api_blueprint', 'prefix':'/api'},
    {'module':abs, 'blueprint':'abs_blueprint', 'prefix':'/abs' },
    {'module':dynamicjs, 'blueprint':'dynjs_blueprint', 'prefix':'/dynjs'},
]

try:
    from adsabs.modules import searchcompare
    _BLUEPRINTS_MODULES.append({'module':searchcompare, 'blueprint':'searchcompare_blueprint', 'prefix':'/searchcompare' })
except ImportError:
    pass

BLUEPRINTS = _BLUEPRINTS_CORE + _BLUEPRINTS_MODULES