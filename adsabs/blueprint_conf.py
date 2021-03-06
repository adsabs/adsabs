
"""
Blueprints to be registered and initialized should be imported here and added to BLUEPRINTS
"""

from adsabs.modules import (search, user, api, abs, index, dynamicjs, 
                            feedback, bibutils, recommender, pages, 
                            redirect, export, visualization, buggyme, adsgut, autocomplete, graphics)

BLUEPRINTS = [index, user, search, api, abs, dynamicjs, feedback, bibutils, recommender, pages, redirect, 
              export, visualization, buggyme, adsgut, autocomplete, graphics]

try:
    from adsabs.modules import searchcompare
    BLUEPRINTS.append(searchcompare)
except ImportError:
    pass
