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

//Remove all the disabled input
$(':input').removeAttr("disabled");

//I add a function on the forms
$("form").submit(function()
{
    $(this).find(':input[value=""]').attr("disabled", "disabled");
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


//function search_form_second_order(sort_menu, obj_drower, obj_drawer_handler)
///*function that checks if in the drop down menu of the sorting the option */
//{
//	//If I have a second order operator
//	if($(sort_menu).val() == 'second_order_operator')
//	{
//		//I preselect the first radio
//		$("input:radio[name=second_order_type]:first").attr('checked', 'checked');
//		//I open the advanced options if they are not already open
//		if ($(obj_drower).is(":hidden"))
//		{
//			$(obj_drower).slideToggle('fast', function(){
//				$(obj_drawer_handler).html('less options');
//			});
//		}
//	}
//	//otherwise I need to uncheck all the radios
//	else
//	{
//		$("input:radio[name=second_order_type]").removeAttr('checked');
//	}
//};
//
//function radio_second_order_type(sort_menu)
///*Function that set the sort dropdown menu if a radio button of the second order operators is selected*/
//{
//	if ($(sort_menu).val() != 'second_order_operator')
//		$(sort_menu).val('second_order_operator');
//};

