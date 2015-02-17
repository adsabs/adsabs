'''
Created on Sep 5, 2014

@author: ehenneken
'''
from flask import (Blueprint, request, url_for, Response, current_app as app, abort, render_template, jsonify, g)
#from flask.ext.solrquery import solr, signals as solr_signals #@UnresovledImport
from config import config
from paper_thumbnails import get_thumbnails
import ptree

graphics_blueprint = Blueprint('graphics', __name__, template_folder="templates", url_prefix='/graphics')


@graphics_blueprint.route('/<bibcode>/<figure_id>/<image_format>', methods=('GET','POST'))
def display_image(bibcode,figure_id,image_format):
    """
    For a given article, figure ID and format, fetch and display the image
    """
    format2ext = {'tb':'gif','lr':'jpg','hr':'png'}
    image_ext = format2ext.get(image_format,'png')
    image_dir = config.IMAGE_PATH + ptree.id2ptree(bibcode)
    image = "%s%s_%s_%s.%s" % (image_dir,bibcode,figure_id,image_format,image_ext)
    try:
        image_data = open(image, "rb").read()
    except Exception, e:
        app.logger.error('ID %s. Unable to get image %s (format: %s) for bibcode : %s! (%s)' % (g.user_cookie_id,figure_id,image_format,bibcode,e))
        return ('', 204)
    header = {'Content-type': 'image/%s'%image_ext}
    return image_data, 200, header

@graphics_blueprint.route('/thumbnails/<bibcode>', defaults={'format': None}, methods=['GET', 'POST'])
@graphics_blueprint.route('/thumbnails/<bibcode>/<format>', methods=['GET', 'POST'])
def thumbnails(bibcode,format):
    """
    View that creates overview of thumbnails with article graphics
    """
    results = {}
    try:
        results = get_thumbnails(bibcode)
    except Exception,e:
        app.logger.error('ID %s. Unable to get thumbnails for bibcode : %s! (%s)' % (g.user_cookie_id,bibcode,e))
        return render_template('recommendations_embedded.html', results={})
    if format == 'json':
        return jsonify(paper=bibcode, graphics=results)
    else:
        return render_template('thumbnails_embedded.html', display=results)