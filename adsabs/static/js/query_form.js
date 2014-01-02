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
			$(obj_drawer_handler).children('i').removeClass('icon-plus').addClass('icon-minus');
		}
		else
		{
			$(obj_drawer_handler).children('i').removeClass('icon-minus').addClass('icon-plus');
		}
	});
};


//code to configure the search form at each load

$(document).ready(function(){
	// alex's note: I don't know what this does and have commented it out for now
	//Remove all the disabled input
	// alex's note: I changed this to touch only the 2.0 form and not the classic form
	// $('#one_box_search:input').removeAttr("disabled");
	
	// //I add a function on the forms
	// $("#one_box_search").submit(function()
	// {
	// 	$(this).find('input, select').filter(function() { return $(this).val() == ""; }).attr("disabled", "disabled");
	//     return true; // ensure form still submits 
	// });
	
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

	$("#one_box_search").on("submit", function(e){
		var start_month = $("#month_from").val()
		var start_year = $("#year_from").val()
		var end_month = $("#month_to").val()
		var end_year = $("#month_to").val()
		if ((start_month && !start_year) || (end_month && !end_year))
		{
			e.preventDefault();
			$(".one_box_search_container").prepend("<div class=\"alert alert-error\" style=\"width:82%\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button><strong>Error!</strong> Month field designated without a corresponding year!</div>")

		}
	})
	
});
