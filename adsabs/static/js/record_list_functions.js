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
        //if I have checked bibcodes
        if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
        {
            // Gather the checked bibcodes
            ResultListManager.checked_bibcodes = new Array();
            var $inputs = $('#search_results_form').find('input[name="bibcode"]:checked');
            $inputs.each(function() {
                ResultListManager.checked_bibcodes.push($(this).attr('value'));
            });
            // Call the Citation Helper with these bibcodes
        if ($('#search_results_form').find('input[name="bibcode"]:checked').length > 0)
        {
                $('#search_results_form').attr('bibcodes', ResultListManager.checked_bibcodes.join("\n")).attr('action', 'http://jadzia:5000/bibutils/citation_helper').submit();
        }
            // Display the results

        }
};