/**
 * 
 */

//###########################################################################################//
//Definition of a new jQuery Method that is an extended version of the $.get
$.getADS = function(url_ads, data_ads, success_ads, error_ads, dataType_ads)
{
	$.ajax({
		type: "GET",
		url: url_ads,
		data: data_ads,
		success: success_ads,
		error: error_ads,
		dataType: dataType_ads,
		timeout: 600000,
	});
};

$.postADS = function(url_ads, data_ads, success_ads, error_ads, dataType_ads)
{
	$.ajax({
		type: "POST",
		url: url_ads,
		data: data_ads,
		success: success_ads,
		error: error_ads,
		dataType: dataType_ads,
		timeout: 600000,
	});
};

//definition of a new jQuery method to set the cursor at a certain point of the textfield
/**** thanks to Mark from StackOverflow ****/
$.fn.selectRange = function(start, end) {
    return this.each(function() {
        if (this.setSelectionRange) {
            this.focus();
            this.setSelectionRange(start, end);
        } else if (this.createTextRange) {
            var range = this.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', start);
            range.select();
        }
    });
};

//definition of an escaping method
RegExp.escape = function(text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
}

//###########################################################################################//

var Misc = new Object();

Misc.wrapText = function(elementID, openTag, closeTag)
/* function to wrap text inside other tags */
/****thanks to richleland from StackOverflow****/
{
    var textArea = $('#' + elementID);
    var len = textArea.val().length;
    var start = textArea[0].selectionStart;
    var end = textArea[0].selectionEnd;
    //if start and end are the same number I take the end of the string
    if (start == end)
    {
    	start = textArea.val().length;
    	end = textArea.val().length;
    }
    var selectedText = textArea.val().substring(start, end);
    var replacement = openTag + selectedText + closeTag;
    textArea.val(textArea.val().substring(0, start) + replacement + textArea.val().substring(end, len));
    
    //then I 
    endrepl = start + replacement.length - closeTag.length;
    textArea.selectRange(endrepl, endrepl);
};