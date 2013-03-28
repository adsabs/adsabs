/**
 * Manager for the tooltips in the page.
 */

var TooltipManager = new Object();

/* Generic function to apply a tooltip to an element
 * Needed to have an unique place where to set up the parameters
 */
TooltipManager.enable_tooltip = function(selector) {
	$(selector).tooltip({
		html : true,
		container : 'body',
		delay : { show: 1600, hide: 100 }
	}).on('show hide', function(event){event.stopPropagation();});
};


/* 
 * By Default I apply the tooltip to all the elements identified by rel=bootstrap_tooltip 
 */
$(document).ready(function(){
	TooltipManager.enable_tooltip('[data-rel=bootstrap_tooltip]');
});