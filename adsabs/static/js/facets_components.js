/**
 * Functions for facets
 */

var FacetsComponents = new Object();

/*
 * Function that manages the facets with only one level
 */
FacetsComponents.sigle_level_manager = function(facetid_html)
{
	//Code to change the icon in the section containing the title of the facets 
	$('#collapse'+facetid_html).on('hide', function() {
		$('#icon'+facetid_html).attr('class', 'icon-chevron-right');
		$('#apply_menu_'+facetid_html).hide();
		
	});
	$('#collapse'+facetid_html).on('show', function() {
		$('#icon'+facetid_html).attr('class', 'icon-chevron-down');
		$('#apply_menu_'+facetid_html).show();
	});
	//Code to show/hide the facets
	var max_facets = 5;
	//if I have hidden facets 
	if ($('#facetList'+facetid_html+' > li:hidden').length > 0)
	{
		//I show the button "more" 
		$('#collapse'+facetid_html+' a.more').show();
		//I configure the "more" to expand the list 
		$('#collapse'+facetid_html+' a.more').on('click', function(){
			//I expand the next N elements 
			var hidden_li = $('#facetList'+facetid_html+' > li:hidden');
			for (var i=0; i<max_facets; i++)
				$(hidden_li[i]).show('fast', function(){
					//If there are no more hidden elements I hide the more button 
					if ($('#facetList'+facetid_html+' > li:hidden').length == 0)
						$('#collapse'+facetid_html+' a.more').hide();
				});
			//I show the "less" anyway because there will be for sure more than N minimum elements 
			if ($('#collapse'+facetid_html+' a.less').is(':hidden'))
				$('#collapse'+facetid_html+' a.less').show();
		});
		//I configure the "less" to collapse the list 
		$('#collapse'+facetid_html+' a.less').on('click', function(){
			var visible_li = $('#facetList'+facetid_html+' > li:visible');
			var to_hide = max_facets;
			//I make sure that I don't hide more than the minimum allowed 
			if ((visible_li.length - max_facets) < max_facets)
				to_hide = visible_li.length - max_facets;
			//I hide the elements 
			for (var i=1; i<=to_hide; i++)
				$(visible_li[visible_li.length - i]).hide('fast', function(){
					//If I've reached the minimum of elements to hide, I hide "less"
					if ($('#facetList'+facetid_html+' > li:visible').length == max_facets)
						$('#collapse'+facetid_html+' a.less').hide();
				});
			//I show "more" if it is hidden 
			if ($('#collapse'+facetid_html+' a.more').is(':hidden'))
				$('#collapse'+facetid_html+' a.more').show();
		});
	}	
}

/*
 * Function that manages the first level of the hierarchical facets
 */
FacetsComponents.hierarchical_level_one_manager = function(facetid_html)
{
	//Code to change the icon in the section containing the title of the facets 
	$('#collapse'+facetid_html).on('hide', function () {
		$('#icon'+facetid_html).attr('class', 'icon-chevron-right');
		$('#apply_menu_'+facetid_html).hide();
	});
	$('#collapse'+facetid_html).on('show', function () {
		$('#icon'+facetid_html).attr('class', 'icon-chevron-down');
		$('#apply_menu_'+facetid_html).show();
	});
	//Code to show/hide the facets
	var max_facets = 5;
	//if I have hidden facets 
	if ($('#facetList'+facetid_html+' > li:hidden').length > 0)
	{
		//I show the button "more" 
		$('#collapse'+facetid_html+' a.more').show();
		//I configure the "more" to expand the list 
		$('#collapse'+facetid_html+' a.more').on('click', function(){
			//I expand the next N elements 
			var hidden_li = $('#facetList'+facetid_html+' > li:hidden');
			for (var i=0; i<max_facets; i++)
				$(hidden_li[i]).show('fast', function(){
					//If there are no more hidden elements I hide the more button 
					if ($('#facetList'+facetid_html+' > li:hidden').length == 0)
						$('#collapse'+facetid_html+' a.more').hide();
				});
			//I show the "less" anyway because there will be for sure more than N minimum elements 
			if ($('#collapse'+facetid_html+' a.less').is(':hidden'))
				$('#collapse'+facetid_html+' a.less').show();
		});
		//I configure the "less" to collapse the list 
		$('#collapse'+facetid_html+' a.less').on('click', function(){
			var visible_li = $('#facetList'+facetid_html+' > li:visible');
			var to_hide = max_facets;
			//I make sure that I don't hide more than the minimum allowed 
			if ((visible_li.length - max_facets) < max_facets)
				to_hide = visible_li.length - max_facets;
			//I hide the elements 
			for (var i=1; i<=to_hide; i++)
				$(visible_li[visible_li.length - i]).hide('fast', function(){
					//If I've reached the minimum of elements to hide, I hide "less"
					if ($('#facetList'+facetid_html+' > li:visible').length == max_facets)
						$('#collapse'+facetid_html+' a.less').hide();
				});
			//I show "more" if it is hidden 
			if ($('#collapse'+facetid_html+' a.more').is(':hidden'))
				$('#collapse'+facetid_html+' a.more').show();
		});
	}
	//Code to see if there are some subfacets that should be open by default
	var open_by_default = $('span.expCollSubFacet'+facetid_html+'.openByDefault');
	if (open_by_default.length > 0)
	{
		for (var i=0; i<open_by_default.length; i++)
			FacetsComponents.hierarchical_level_two_builder(open_by_default[i]);
	}
};

/*
 * Function that creates the second level of hierarchical facets
 */
FacetsComponents.hierarchical_level_two_builder = function(node_obj)
{
	//first of all I change the icon after I click
	$(node_obj).toggleClass('icon-chevron-right');
	$(node_obj).toggleClass('icon-chevron-down');
	//I toggle the visibility of the second level
	var id_sublevel = $(node_obj).data('id_sublevel');
	$('#'+id_sublevel).toggleClass('in');
	//I check if I already fetched the content of the second level
	if ($(node_obj).data('sublevel_facets') === undefined)
	{
		//I start a spin
		$('#'+id_sublevel).html('&nbsp;').spin('ads_facets');
		//I define the url to query
		var url_to_query = GlobalVariables.FACETS_REQUESTS+'?'+$(node_obj).data('query_params_url')+'&facet_field='+$(node_obj).data('templ_facetid')+'&facet_prefix='+$(node_obj).data('facet_prefix_next_level');
		$.get(url_to_query)
			.done(function(response){
				//I insert the data in the DOM
				$('#'+id_sublevel).html(response);
				//I change some css for the div hat contains the sub-facets
				$('#'+id_sublevel).removeClass('emptySubFacets');
				//I set a parameter to remember that the facets have been already loaded
				$(node_obj).data('sublevel_facets', true);
			})
			.fail(function(){
				$('#'+id_sublevel).html('Error retrieving facets');
			})
			.always(function(){
				//I stop the spin
				$('#'+id_sublevel).spin(false);
			});
	}
};


/*
 * Function that manages the behaviour of the facets in the second level
 */
FacetsComponents.hierarchical_level_two_manager = function(facetid_html)
{
	//Code to show/hide the facets
	var max_facets = 5;
	if ($('li.'+facetid_html+':hidden').length > 0)
	{
		//I show the button "more"
		$('#more_'+facetid_html).show();
		//I attach a function to show the elements
		$('#more_'+facetid_html).on('click', function(){
			//I show the  additional elements 
			var to_show = $('li.'+facetid_html+':hidden');
			for (var j=0; j<max_facets; j++)
				$(to_show[j]).show();
			//I show the less button if it was hidden
			if ($('#less_'+facetid_html).is(':hidden'))
				$('#less_'+facetid_html).show();
			//if there is nothig hidden I hide the more button
			if ($('li.'+facetid_html+':hidden').length == 0)
				$(this).hide();
		});
		//I attach a function to hide the elements
		$('#less_'+facetid_html).on('click', function(){
			var visible_li = $('li.'+facetid_html+':visible');
			var to_hide = max_facets;
			//I make sure that I don't hide more than the minimum allowed 
			if ((visible_li.length - max_facets) < max_facets)
				to_hide = visible_li.length - max_facets;
			for (var i=1; i<=to_hide; i++)
				$(visible_li[visible_li.length - i]).hide();
			//I show the more button if it is hidden 
			if ($('#more_'+facetid_html).is(':hidden'))
				$('#more_'+facetid_html).show();
			//If I reached the minimum number of visible elements I hide the less
			if ($('li.'+facetid_html+':visible').length == max_facets)
				$(this).hide();
		})
	}
};


/*
 * Function that handles the selection of multiple facets in the same group
 */
FacetsComponents.multiple_facet_selection = function(node_obj)
{
	//I get the value of the current checkbox and I add/remove it to the list of selected checkboxes
	var facetid_html = $(node_obj).data('facetid_html');
	//I extract the original version of the facet id: I need it because the facet id for some facets is different from the one displayed in the interface (i.e. refereed and properties in general)
	var facetid_orig = $(node_obj).data('facetid_original');
	if (facetid_orig === undefined)
		facetid_orig = null
	var cur_value = $(node_obj).data('value');
	var cur_selection = $('#facetForm_'+facetid_html).data('selected_checkbox_facets');
	if ($(node_obj).is(':checked'))
		cur_selection[cur_value] = true;
	else
		delete cur_selection[cur_value];
	
	//then I call the function to manage the button for the options to apply
	this.apply_facet_manager(facetid_html, facetid_orig);
};

/*
 * Function that manages tha "apply" button of a group of facets
 */
FacetsComponents.apply_facet_manager = function(facetid_html, facetid_orig)
{
	//I get the list of selected facets
	var cur_selection = $('#facetForm_'+facetid_html).data('selected_checkbox_facets');
	//if the number of selected facets is == 0 I disable the "apply menu" 
	if (Object.keys(cur_selection).length == 0)
	{
		if (!$('#apply_menu_'+facetid_html+'>ul>li.op_excl').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+'>ul>li.op_excl').addClass('disabled').on('click', function(){return false;});
		if (! $('#apply_menu_'+facetid_html+' >a').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+' >a').addClass('disabled');
	}
	//if the number of selected facets is == 1 I enable the "apply menu" with only the exclude
	else if (Object.keys(cur_selection).length == 1)
	{
		if ($('#apply_menu_'+facetid_html+' >a').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+' >a').removeClass('disabled');
		if ($('#apply_menu_'+facetid_html+'>ul>li.op_excl').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+'>ul>li.op_excl').removeClass('disabled').on('click', function(event){FacetsComponents.apply_facet_url_manager(facetid_html, facetid_orig, 'EXCL'); event.stopPropagation();});
		//I disable the and and or
		if (!$('#apply_menu_'+facetid_html+'>ul>li.op_and').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+'>ul>li.op_and').addClass('disabled').on('click', function(){return false;});
		if (!$('#apply_menu_'+facetid_html+'>ul>li.op_or').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+'>ul>li.op_or').addClass('disabled').on('click', function(){return false;});
	}
	//if the number is > 1 I enable the full menu
	else if (Object.keys(cur_selection).length > 1)
	{
		if ($('#apply_menu_'+facetid_html+' >a').hasClass('disabled'))
			$('#apply_menu_'+facetid_html+' >a').removeClass('disabled');
		//I add the onclick to "and" and "or"
		$('#apply_menu_'+facetid_html+'>ul>li.op_and').removeClass('disabled').on('click', function(event){FacetsComponents.apply_facet_url_manager(facetid_html, facetid_orig, 'AND'); event.stopPropagation();});
		$('#apply_menu_'+facetid_html+'>ul>li.op_or').removeClass('disabled').on('click', function(event){FacetsComponents.apply_facet_url_manager(facetid_html, facetid_orig, 'OR'); event.stopPropagation();});
	}
};

/*
 * Function that manages the actual creation of a new url for the selected facets based on the kind of selection
 */
FacetsComponents.apply_facet_url_manager = function(facetid_html, facetid_orig, op_type)
{
	op_type = op_type.toUpperCase();
	//I get the object containing the selected facets
	var cur_selection = Object.keys($('#facetForm_'+facetid_html).data('selected_checkbox_facets'));
	//then I create the url for the facets to apply
	var location_url = window.location.href+'&';
	if (facetid_orig == null)
		location_url += facetid_html;
	else
		location_url += facetid_orig;
	location_url += '=(';
	for (var idx in cur_selection)
	{
		if (op_type != 'EXCL')
			location_url += encodeURIComponent('"'+cur_selection[idx]+'"');
		else
			location_url += encodeURIComponent('-"'+cur_selection[idx]+'"');
		if (idx < (cur_selection.length-1))
		{
			if ((op_type == 'AND') || (op_type == 'OR'))
				location_url += '+' + op_type + '+';
			else if (op_type == 'EXCL')
				location_url += '+AND+';
		}
	}
	location_url +=')';
	window.location = location_url.replace('%20', '+').replace(' ', '+');
};



