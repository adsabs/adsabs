
jQuery.ajaxSetup({
	  beforeSend: function() {
	     $('div.resultsSpinner').show();
	  },
//	  complete: function(){
//	     $('div.resultsSpinner').hide();
//	  },
//	  error: function(x, status, error) {
//		 console.log("status: " + status + ", error: " + error); 
//	  }
//	  success: function() { 
//		  console.log("success!"); 
//	  }
	});

// jquery-bbq stuff...
$(window).bind( 'hashchange', function(e) {
    var hashQuery = jQuery.deparam.fragment();
    if (hashQuery.classic || hashQuery.solr) {
        $("#input-classic").val(hashQuery.classic);
        $("#input-solr").val(hashQuery.solr);
    }
});
 
$(document).ready(function() {
	$("#search-button").bind('click', function(e) {
		$("div#results-classic").empty();
		$('div#results-solr').empty();
		var classicQuery = $("#input-classic").val();
		var solrQuery = $("#input-solr").val();
		location.href = jQuery.param.fragment( location.href, {classic: classicQuery, solr: solrQuery});
		$("div#results-classic").load('/searchcompare/classic?q=' + encodeURIComponent(classicQuery), function() {
			$('div#results-classic').siblings('.resultsSpinner').hide();
		});
		$("div#results-solr").load('/searchcompare/solr?q=' + encodeURIComponent(solrQuery), function() {
			$('div#results-solr').siblings('.resultsSpinner').hide();
		});
	})
	$(window).trigger( 'hashchange' );
});
