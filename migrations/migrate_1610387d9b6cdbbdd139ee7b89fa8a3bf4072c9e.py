"""
updates ads_users api permission developer perms to change 'full' field to 'body'
"""
from adsabs.extensions import mongodb
from flask import current_app as app

def migrate():
    db = mongodb.session.db
    result = db.ads_users.update(
        {'$where': 'this.developer_key.length > 0'},
        {'$addToSet': {'developer_perms.highlight_fields': 'body'}},
        multi=True
    )
    app.logger.info("migration operation result: %s" % str(result))
    result = db.ads_users.update(
        {'$where': 'this.developer_key.length > 0'},
        {'$pull': {'developer_perms.highlight_fields': 'full'}},
        multi=True
    )
    app.logger.info("migration operation result: %s" % str(result))