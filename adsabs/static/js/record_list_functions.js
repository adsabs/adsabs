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