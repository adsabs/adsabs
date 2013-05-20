/**
 * functions to manage the feedback form in a fancybox
 */

var FeedbackManager = new Object();

/*Function that shows the feedback button to the page*/
FeedbackManager.append_feedback_button = function(){
	if ($(window).width() >= 1000 && $(window).height() >= 700)
	{
		if ($('#feedback_widget').hasClass('hidden_elem'))
			$('#feedback_widget').removeClass('hidden_elem');
	}
	else
	{
		if (!$('#feedback_widget').hasClass('hidden_elem'))
			$('#feedback_widget').addClass('hidden_elem');
	}
};

/* Check if it possible to show the feedback button and 
 * append a function to check again at every page resize
 */
$(document).ready(function(){
	//check if I can show the button
	FeedbackManager.append_feedback_button();
	//append the event on the window resize
	$(window).resize(function(){
		FeedbackManager.append_feedback_button();
	})
	//enable the fancybox button
	$('#button_feedback_widget').fancybox();
});