/**
 * functions to manage the feedback form in a fancybox
 */

var FeedbackManager = function() {
	return {
		
		/*Function that shows the feedback button to the page*/
		append_feedback_button: function(){
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
		},
		
		get_href: function(req_mode) {
			var req_mode = req_mode || "";
			var feedbackUri = new Uri(GlobalVariables.FEEDBACK_URL)
								.addQueryParam('feedb_req_mode', req_mode)
								.addQueryParam('page_url', encodeURIComponent(location.href));
			return feedbackUri.toString();
		},

		set_fancybox_href: function() {
			$('#button_feedback_widget').attr('data-fancybox-href', this.get_href('nolayout'));
		},
		
		set_topnav_link: function() {
			$('#feedback-topnav').on('click', function() {
				window.location = FeedbackManager.get_href();
			});
		}
	}
}();


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
	FeedbackManager.set_topnav_link();
	FeedbackManager.set_fancybox_href();
	//enable the fancybox button
	$('#button_feedback_widget').fancybox();
});