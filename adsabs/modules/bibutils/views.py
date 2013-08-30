'''
Created on Jul 16, 2013

@author: ehenneken
'''

from .forms import CitationHelperInputForm
from .forms import MetricsInputForm
from flask import (Blueprint, render_template, flash, request, jsonify, g, current_app as app)
from adsabs.core.form_functs import is_submitted_cust
from config import config #the global config object
from .biblio_functions import get_suggestions
from .metrics_functions import generate_metrics
from .errors import CitationHelperCannotGetResults

__all__ = ['bibutils_blueprint', 'index_bibutils', 'citation_helper','metrics']

bibutils_blueprint = Blueprint('bibutils', __name__, template_folder="templates", url_prefix='/bibutils')

@bibutils_blueprint.route('/', methods=('GET','POST'))
def index_bibutils():
    """
    Entry point of input for ADS Bibliographic Utilities: currently only Citation Helper
    """
    return render_template('index_bibutils.html', page_var='ADS Bibliographic Utilities')

@bibutils_blueprint.route('/citation_helper', methods=('GET','POST'))
def citation_helper(**args):
    """
    Entry point of input for Citation Helper: form to input bibcodes
    """
    form = CitationHelperInputForm()
    # If we were called from results form, get bibcodes
    # from URL
    try:
        bibcodes = request.args.getlist('bibcode')
    except:
        bibcodes = []
    results = None
    format = ''
    # check if we were called with bibcodes
    if 'bibcodes' in args:
        bibcodes = args['bibcodes']
        format = 'json'
    if 'Nsuggest' in args:
        number_of_suggestions = args['Nsuggest']
    else:
        number_of_suggestions = config.BIBUTILS_DEFAULT_SUGGESTIONS
    if is_submitted_cust(form):
        # the form was submitted, so get the contents from the submit box
        # make sure we have a list of what seem to be bibcodes
        bibcodes = map(lambda a: str(a).strip(), form.bibcodes.data.strip().split('\n'))
        bibcodes = filter(lambda a: len(a) == 19, bibcodes)
        # no bibcodes? display message and re-display input form
        if len(bibcodes) == 0:
            flash('Citation Helper returned no results. Reason: No bibcodes were supplied')
            return render_template('citation_helper.html', form=form)
        # get the maximum number of suggestions
        number_of_suggestions = int(form.return_nr.data)
        app.logger.info('ID %s. Requesting %s suggestions. Input: %s'%(g.user_cookie_id,number_of_suggestions,str(bibcodes)))
    if len(bibcodes) > 0:
        # we have all we need, so it's time to get the suggestions
        try:
            suggestions = get_suggestions(bibcodes=bibcodes,Nsuggest=number_of_suggestions)
        except CitationHelperCannotGetResults, e:
            # if we end up here, something went boink during data retrieval
            app.logger.error('ID %s. Unable to get results! (%s)' % (g.user_cookie_id,e))
        # if we got results, return them, otherwise say that we did not find any,
        # and re-display the input form.
        # no suggestions are possible if there are no 'friends-of-friends'
        if len(suggestions) > 0:
            app.logger.info('ID %s. Found %s suggestions. Suggestions: %s'%(g.user_cookie_id,len(suggestions),str(suggestions)))
            if format == 'json':
                return jsonify(suggestions=suggestions)
            else:
                return render_template('citation_helper_results.html', page_var='Citation Helper Results', results=suggestions)
        else:
            app.logger.info('ID %s. No suggestions found.'%g.user_cookie_id)
            if format == 'json':
                return jsonify(suggestions=suggestions)
            else:
                flash('Citation Helper returned no results. Reason: No suggestions were found.')
    return render_template('citation_helper.html', form=form)

@bibutils_blueprint.route('/metrics', methods=('GET','POST'))
def metrics(**args):
    """
    Entry point of input for Metrics: form to input bibcodes
    """
#     query = request.args.get('q', None)
    form = MetricsInputForm()
    bibcodes = []
    results = None
    format = ''
    if 'bibcodes' in args:
        bibcodes = args['bibcodes']
        format = 'json'
    if is_submitted_cust(form):
        # the form was submitted, so get the contents from the submit box
        # make sure we have a list of what seem to be bibcodes
        bibcodes = map(lambda a: str(a).strip(), form.bibcodes.data.strip().split('\n'))
        bibcodes = filter(lambda a: len(a) == 19, bibcodes)
        # no bibcodes? display message and re-display input form
        if len(bibcodes) == 0:
            flash('Metrics returned no results. Reason: No valid bibcodes were supplied')
            return render_template('metrics.html', form=form)
    if len(bibcodes) > 0:
        # we have a list of bibcodes, so start working
        try:
            results = generate_metrics(bibcodes=bibcodes, types='statistics,histograms,metrics,series', fmt=format)
        except Exception, err:
            app.logger.error('ID %s. Unable to get results! (%s)' % (g.user_cookie_id,err))
    if results:
        if format == 'json':
            return jsonify(metrics=results)
        else:
            return render_template('metrics_results.html', results=results)
    return render_template('metrics.html', form=form)
