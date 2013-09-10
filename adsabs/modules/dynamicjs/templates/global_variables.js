/**
 * Object containig global variables
 */

var GlobalVariables = new Object();

//variable containig the url for ajax requests for the facets

GlobalVariables.FACETS_REQUESTS = '{{ url_for("search.facets") }}';

GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL = '{{ config.ADS_CLASSIC_BASEURL }}/cgi-bin/nph-abs_connect';

GlobalVariables.ADSABS2_CITATION_HELPER_BASE_URL = '{{ url_for("bibutils.citation_helper") }}';

GlobalVariables.ADSABS2_METRICS_BASE_URL = '{{ url_for("bibutils.metrics") }}';
