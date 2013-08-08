/**
 * 
 */

function search_form_drawer_manager(obj_drower, obj_drawer_handler)
/*function to open and close the drawer*/
{
	//I open the drawer
	$(obj_drower).slideToggle('fast', function(){
		//I check if the drawer is visible or not
		if ($(obj_drower).is(":visible"))
		{
			$(obj_drawer_handler).html('<i class="icon-minus"></i>');
			$(obj_drawer_handler).attr('title', 'less options');
		}
		else
		{
			$(obj_drawer_handler).html('<i class="icon-plus"></i>');
			$(obj_drawer_handler).attr('title', 'more options');
		}
	});
};


//code to configure the search form at each load

$(document).ready(function(){
	//Remove all the disabled input
	$(':input').removeAttr("disabled");
	
	//I add a function on the forms
	$("form").submit(function()
	{
		$(this).find('input, select').filter(function() { return $(this).val() == ""; }).attr("disabled", "disabled");
	    return true; // ensure form still submits 
	});
	
	//if there are input in the advanced options that are filled in, I show the advanced options
	var advanced_params_text = $("#advanced_options :input[type=text]");
	var advanced_params_check = $("#advanced_options :input[type=checkbox]");
	for (var x=0; x<advanced_params_text.length; x++)
	{
		if ($(advanced_params_text[x]).val() != '')
		{
			search_form_drawer_manager($("#advanced_options"), $("#drawer_handler"));
			break;
		}
	}
	for (var x=0; x<advanced_params_check.length; x++)
	{
		if ($(advanced_params_check[x]).attr('checked') == 'checked')
		{
			search_form_drawer_manager($("#advanced_options"), $("#drawer_handler"));
			break;
		}
	}
	
	//code for the "search settings" menu
	$('.add-open-permanent').on('click', function(e) {
		$(this).parents('.dropdown').addClass('open-permanent')
	});
		
	$(document).on('click', function(e) {
		if ($(e.target).parents('.donothide').length <= 0) 
		{
			$('.open-permanent').removeClass('open-permanent')
		}
	});

	$('select.buttonSelect').buttonSelect({
		button: '<div class="btn btn-mini" />', 
		span: '<span class="btn btn-mini" style="width: 80px;" />',
		next: '<i class="icon icon-plus"></i>',
		prev: '<i class="icon icon-minus"></i>',
	});
	
});
