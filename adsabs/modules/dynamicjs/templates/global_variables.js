/**
 * Object containig global variables
 */

var GlobalVariables = new Object();

//variable containig the url for ajax requests for the facets
GlobalVariables.FACETS_REQUESTS = '{{ url_for("search.facets") }}';
//variable with the url to export the records to ADS Classic
GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL = '{{ config.ADS_CLASSIC_BASEURL }}/cgi-bin/nph-abs_connect';
//variable containing the number of records to show in ADS Classic after the export
GlobalVariables.ADS_CLASSIC_EXPORT_NR_TO_RETURN = {{ config.EXPORT_DEFAULT_ROWS }};
//variable with the url of the view to get only bibcodes from a query
GlobalVariables.ADSABS2_GET_BIBCODES_ONLY_FROM_QUERY = '{{ url_for("export.get_bibcodes_from_query") }}';
//Variable with the url of the view to export the bibcodes in other formats
GlobalVariables.ADSABS2_EXPORT_TO_OTHER_FORTMATS_BASE_URL = '{{ url_for("export.export_to_other_formats") }}';

GlobalVariables.ADSABS2_CITATION_HELPER_BASE_URL = '{{ url_for("bibutils.citation_helper") }}';

GlobalVariables.ADSABS2_METRICS_BASE_URL = '{{ url_for("bibutils.metrics") }}';

GlobalVariables.ADSABS2_METRICS_ALT_BASE_URL = 'http://adsabs.harvard.edu/tools/metrics/';