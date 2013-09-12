/**
 * Functions to manage the list of results
 */

ResultListManager = new Object();

/*
 * Function to export a list of selected papers to ads classic
 */
ResultListManager.export_to_ads_classic = function()
{
	//if I have checked bibcodes
	if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
	{
		$('#search_results_form').attr('action', GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL).attr('target', '_blank').submit();
	}
};
/*
 * Function to get Citation Helper results
 */
ResultListManager.citation_helper = function()
{
        $.fancybox.showLoading();
        //re-enable query parameters
        $('#search_results_form > input[name="current_search_parameters"]').removeAttr('disabled');
        //remove a hidden fields if exists
        $('#search_results_form > input.ajaxHiddenField').remove();
        //if there are checked bibcodes
        if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
        {
                //remove the query parameters
                checked_bibcodes = new Array();
                var $inputs = $('#search_results_form').find('input[name="bibcode"]:checked');
                $inputs.each(function() {
                    checked_bibcodes.push($(this).attr('value'));
                });
                var collapsed_bibcodes = checked_bibcodes.join('\n');
        }
        else
        {
                bibcodes = new Array();
                var $inputs = $('#search_results_form').find('input[name="bibcode"]');
                $inputs.each(function() {
                    bibcodes.push($(this).attr('value'));
                });
                var collapsed_bibcodes = bibcodes.join('\n');
        }
        $('#search_results_form > input[name="current_search_parameters"]').attr('disabled','disabled');
        $('#search_results_form').append('<input type="hidden" name="bibcodes" class="ajaxHiddenField"  value="'+collapsed_bibcodes+'"/>');
        $('#search_results_form').append('<input type="hidden" name="return_nr" class="ajaxHiddenField"  value="10"/>');
        //submit the form via ajax
        $.ajax({
                type : "POST",
                cache : false,
                url : GlobalVariables.ADSABS2_CITATION_HELPER_BASE_URL,
                data : $('#search_results_form').serializeArray(),
                success: function(data) {
                    $.fancybox.hideLoading();
                    $.fancybox(data);
                } 
        });
};
/*
 * Function to get Metrics results
 */
ResultListManager.metrics = function()
{
        $.fancybox.showLoading();
        //re-enable query parameters
        $('#search_results_form > input[name="current_search_parameters"]').removeAttr('disabled');
        //remove a hidden fields if exists
        $('#search_results_form > input.ajaxHiddenField').remove();
        //if there are checked bibcodes
        if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
        {
                //remove the query parameters
                checked_bibcodes = new Array();
                var $inputs = $('#search_results_form').find('input[name="bibcode"]:checked');
                $inputs.each(function() {
                    checked_bibcodes.push($(this).attr('value'));
                });
                var collapsed_bibcodes = checked_bibcodes.join('\n');
        }
        else
        {
                bibcodes = new Array();
                var $inputs = $('#search_results_form').find('input[name="bibcode"]');
                $inputs.each(function() {
                    bibcodes.push($(this).attr('value'));
                });
                var collapsed_bibcodes = bibcodes.join('\n');
        }        $('#search_results_form > input[name="current_search_parameters"]').attr('disabled','disabled');
        $('#search_results_form').append('<input type="hidden" name="bibcodes" class="ajaxHiddenField" value="'+collapsed_bibcodes+'"/>');
        //submit the form via ajax
        $.ajax({
                type : "POST",
                cache : false,
                url : GlobalVariables.ADSABS2_METRICS_BASE_URL,
                data : $('#search_results_form').serializeArray(),
                success: function(data) {
                    $.fancybox.hideLoading();
                    $.fancybox(data);
                }
        });
};
