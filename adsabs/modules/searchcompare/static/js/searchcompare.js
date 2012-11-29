
jQuery.ajaxSetup({
	  beforeSend: function() {
	     $('div.resultsSpinner').show();
	  }
	});

// jquery-bbq stuff...
$(window).bind( 'hashchange', function(e) {
    var hashQuery = jQuery.deparam.fragment();
    if (hashQuery.classic || hashQuery.solr) {
        $("#input-classic").val(hashQuery.classic);
        $("#input-solr").val(hashQuery.solr);
    }
});
 
function generateDiff() {
	var classicBibs = $.map( $("#results-classic .bibcode"), function(el) { return $(el).text() }).join("\n");
	var solrBibs = $.map( $("#results-solr .bibcode"), function(el) { return $(el).text() }).join("\n");
	var classicText = difflib.stringAsLines(classicBibs);
	var solrText = difflib.stringAsLines(solrBibs);
	var sm = new difflib.SequenceMatcher(classicText, solrText);
	var opcodes = sm.get_opcodes();
	$("#diff-display").empty();
	$("#diff-display").append(diffview.buildView({
		baseTextLines: classicText,
		newTextLines: solrText,
		opcodes: opcodes,
		baseTextName: "Classic",
		newTextName: "Solr",
	}));
}

$(document).ready(function() {
	$("#search-button").bind('click', function(e) {
		$("div#results-classic").empty();
		$('div#results-solr').empty();
		var classicQuery = $("#input-classic").val();
		var classicUrl = '/searchcompare/classic?q=' + encodeURIComponent(classicQuery);
		var solrQuery = $("#input-solr").val();
		var solrUrl = '/searchcompare/solr?q=' + encodeURIComponent(solrQuery);
		location.href = jQuery.param.fragment( location.href, {classic: classicQuery, solr: solrQuery});
		
		var classicReq = $.get(classicUrl, function(data) {
			$("#results-classic").html(data)
		}).then(function() {
			$("#classic-spinner").hide();
		}); 
		
		var solrReq = $.get(solrUrl, function(data) {
			$("#results-solr").html(data)
		}).then(function() {
			$("#solr-spinner").hide();
		});
		
		$.when(classicReq, solrReq).then(function() {
			$("#compare-tools").show();
		})
		
	});
	$("#diff-button").bind('click', function(e) {
		generateDiff();
		$("#diff-display").showpopup({
			enableclose: true,
			ismodal: true,
			draggable: true,
			hideOnClick: true,
			overlayStyle: {
				opacity: 0.1,
				background: '#000'
			},
			popupStyle: {
				border:3,
				bordercolor:"#000",
				borderradius:10,
				background:"#ddd"
			}
		});
	});
	$(window).trigger( 'hashchange' );
});
