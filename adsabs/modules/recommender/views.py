'''
Created on Jul 16, 2013

@author: ehenneken
'''
from flask import (Blueprint, render_template, flash, g, jsonify, current_app as app)
from adsabs.core.form_functs import is_submitted_cust
from config import config #the global config object
from .forms import SuggestionsInputForm
from .utils import get_recommendations
from .utils import get_suggestions
from .errors import RecommenderCannotGetResults

__all__ = ['recommender_blueprint','recommender','suggestions']

recommender_blueprint = Blueprint('recommender', __name__, template_folder="templates", url_prefix='/recommender')

@recommender_blueprint.after_request
def add_caching_header(response):
    """
    Adds caching headers
    """
    if not config.DEBUG:
        cache_header = 'max-age=3600, must-revalidate'
    else:
        cache_header = 'no-cache'
    response.headers.setdefault('Cache-Control', cache_header)
    return response

#@recommender_blueprint.route('/', methods=('GET','POST'))
#def index_recommender():
#    """
#    Entry point of input for ADS Recommender Utilities
#    """
#    return render_template('index_recommender.html', page_var='ADS Recommender Utilities')
#
#@recommender_blueprint.route('/recommender/<bibcode>', defaults={'format': None}, methods=('GET','POST'))
#@recommender_blueprint.route('/recommender/<bibcode>/<format>', methods=('GET','POST'))
@recommender_blueprint.route('/<bibcode>', defaults={'format': None}, methods=('GET','POST'))
@recommender_blueprint.route('/<bibcode>/<format>', methods=('GET','POST'))
def recommender(bibcode,format):
    """
    Get recommended articles for a given bibcode in a particular format
    """
    try:
        results = get_recommendations(bibcode=bibcode)
    except RecommenderCannotGetResults, e:
        app.logger.error('ID %s. Unable to get results! (%s)' % (g.user_cookie_id,e))
    if format == 'json':
        return jsonify(paper=bibcode, recommendations=results['recommendations'])
    elif format == 'python':
        return results['recommendations']
    elif format == 'ascii':
        return "\n".join([item['bibcode'] for item in results['recommendations']])
    elif format == 'embedded_html':
        return render_template('recommendations_embedded.html', results=results)
    else:
        return render_template('recommendations.html', results=results)

@recommender_blueprint.route('/personal/', defaults={'cookie': None, 'format': None}, methods=('GET','POST'))
@recommender_blueprint.route('/personal/<cookie>', defaults={'format': None}, methods=('GET','POST'))
@recommender_blueprint.route('/personal/<cookie>/<format>', methods=('GET','POST'))
def suggestions(cookie,format):
    """
    Get personal suggestions from recently viewed articles
    """
    bibcodes = []
    if not cookie: cookie = None
    form = SuggestionsInputForm()
    if is_submitted_cust(form):
        # the form was submitted, so get the contents from the submit box
        # make sure we have a list of what seem to be bibcodes
        bibcodes = map(lambda a: str(a).strip(), form.bibcodes.data.strip().split('\n'))
        bibcodes = filter(lambda a: len(a) == 19, bibcodes)
        # no bibcodes? display message and re-display input form
        if len(bibcodes) == 0:
            flash('No bibcodes were supplied')
            return render_template('suggestions.html', form=form)
    elif not cookie and len(bibcodes) == 0:
        return render_template('suggestions.html', form=form)
    try:
        results = get_suggestions(cookie=cookie,bibcodes=bibcodes)
    except RecommenderCannotGetResults, e:
        app.logger.error('ID %s. Unable to get results! (%s)' % (g.user_cookie_id,e))
    if format == 'json':
        return jsonify(type="from recently viewed", recommendations=results['recommendations'])
    elif format == 'python':
        return results['recommendations']
    elif format == 'ascii':
        return "\n".join([item['bibcode'] for item in results['recommendations']])
    else:
        return render_template('suggestions_results.html', results=results)