
/**
 * module to manage the list of results
 */

ResultListManager = new Object();

/*
 * Function to export a list of selected papers or a query to ads classic
 */
ResultListManager.export_to_ads_classic = function()
{
	//remove a hidden fields if exists
	$('#search_results_form > input.ajaxHiddenField').remove();
	//disable sorting for ADS Classic
	$('#search_results_form').append('<input type="hidden" name="sort" class="ajaxHiddenField" value="NONE"/>');
	
	//if there are checked bibcodes there is nothing to do but submitting the form
	if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
	{
		//remove the query parameters
		$('#search_results_form > input[name="current_search_parameters"]').attr('disabled','disabled');
		//submit the form
		$('#search_results_form').attr('action', GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL).attr('target', '_blank').submit();
	}
	//otherwise need to retrieve the list and then submit the form
	else
	{
		$.fancybox.showLoading();
		
		//re-enable query parameters
		$('#search_results_form > input[name="current_search_parameters"]').removeAttr('disabled');
		//get the bibcodes
		$.ajax({
			type : "POST",
			cache : false,
			url : GlobalVariables.ADSABS2_GET_BIBCODES_ONLY_FROM_QUERY,
			data : $('#search_results_form').serializeArray(),
			success: function(data) {
				$.fancybox.hideLoading();
				//remove the query parameters
				$('#search_results_form > input[name="current_search_parameters"]').attr('disabled','disabled');
				//append an hidden parameter for the bibcodes retrieved
				$('#search_results_form').append('<input type="hidden" name="bibcode" class="ajaxHiddenField" value="'+data+'"/>');
				$('#search_results_form').append('<input type="hidden" name="nr_to_return" class="ajaxHiddenField" value="'+GlobalVariables.ADS_CLASSIC_EXPORT_NR_TO_RETURN+'"/>');
				//submit the form
				$('#search_results_form').removeAttr('target').attr('action', GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL).submit();
			}
		});
	}
		
	
};

/*
 * Function to export a list of papers or a query in different formats
 */
ResultListManager.export_records_in_other_format = function(format)
{	
	$.fancybox.showLoading();
	//re-enable query parameters
	$('#search_results_form > input[name="current_search_parameters"]').removeAttr('disabled');
	//remove a hidden fields if exists
	$('#search_results_form > input.ajaxHiddenField').remove();
	//append the format to the form
	$('#search_results_form').append('<input type="hidden" name="export_format" class="ajaxHiddenField"  value="'+format+'"/>');
	
	//if there are checked bibcodes
	if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
	{
		//remove the query parameters
		$('#search_results_form > input[name="current_search_parameters"]').attr('disabled','disabled');
	}
	
	//submit the form via ajax
	$.ajax({
		type : "POST",
		cache : false,
		url : GlobalVariables.ADSABS2_EXPORT_TO_OTHER_FORTMATS_BASE_URL,
		data : $('#search_results_form').serializeArray(),
		success: function(data) {
			$.fancybox.hideLoading();
			$.fancybox('<pre>'+data+'</pre>');
		}
	});
	
};

/*
 * load a visualization into fancybox
 */
ResultListManager.visualize = function(url) {
	
	$.fancybox.showLoading();
	//re-enable query parameters
	$('#search_results_form > input[name="current_search_parameters"]').removeAttr('disabled');
	//remove a hidden fields if exists
	$('#search_results_form > input.ajaxHiddenField').remove();
	
	//submit the form via ajax
	$.ajax({
		type : "POST",
		cache : false,
		url : url,
		data : $('#search_results_form').serializeArray(),
		success: function(data) {
			$.fancybox.hideLoading();
			$.fancybox(data);
		}
	});
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
        }        
        $('#search_results_form > input[name="current_search_parameters"]').attr('disabled','disabled');
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
