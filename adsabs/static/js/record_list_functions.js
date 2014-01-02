
/**
 * module to manage the list of results
 */

var ResultListManager = function() {

	return {

		remove_hidden: function() {
                //remove a hidden fields if exists
                $('input.ajaxHiddenField', $('#search_results_form')).remove();
		},

		disable_sorting: function() {
			//disable sorting for ADS Classic
			$('#search_results_form').append('<input type="hidden" name="sort" class="ajaxHiddenField" value="NONE"/>');
		},

		add_hidden_field: function(name, value) {
			$('#search_results_form').append('<input type="hidden" name="'+name+'" class="ajaxHiddenField"  value="'+value+'"/>');
		},

		bibcodes_checked: function() {
			return $('#search_results_form').find('input[name="bibcode"]:checked');
		},
		
		bibcodes_displayed: function() {
			return $('#search_results_form').find('input[name="bibcode"]');
		},
		
		is_abstract_page: function() {
			return $('#abstractContent').length ? true : false;
		},
		
		disable_query_params: function() {
			$('input[name="current_search_parameters"]', $('#search_results_form')).attr('disabled','disabled');
		},
		
		enable_query_params: function() {
			$('input[name="current_search_parameters"]', $('#search_results_form')).removeAttr('disabled');
		},
		
		submit_form: function(action) {
			$('#search_results_form').attr('action', action).attr('target', '_blank').submit();
		},
		
		/*
		 * function for getting a integer count of number of records to submit to one of the various
		 * visualizations or analysis generators. takes a callback that will be passed the number
		 * of records supplied by the user when the "OK" button is pressed.
		 */
		record_input_dialog: function(service, ok_callback) {
	        var max_records = GlobalVariables.MAX_EXPORTS[service];
	        var default_records = GlobalVariables.DEFAULT_EXPORTS[service];
	        var hits = parseInt($('#hits').val());
	        $("#amount").val(hits);
	        max_records = Math.min(hits, max_records);
	        if (hits <= max_records) {
	            default_records = max_records
	        };			
	        $( "#record_slider" ).slider({range: "max", min: 1, max: max_records, value: default_records, slide: function( event, ui ) {$( "#amount" ).val( ui.value );}});
	        $( "#amount" ).val( $( "#record_slider" ).slider( "value" ) );
	        $( "#amount" ).show();
	        var dialog = $('#record_selection_dialog').dialog({
	        	title: 'Select number of records',
	        	modal: true,
	        	buttons: {
	        		"OK": function() {
	        			var numRecords = $( "#record_slider" ).slider( "value" );
	        			$(this).dialog('close');
	        			ok_callback(numRecords);
	        		},
                    "Cancel": function() {
                    	$(this).dialog('close');
                    }
	        	}
	        });
        },

        /*
         * submit the search_results_form to a provided url
         * url - ajax request will be sent to this url
         * wrap_pre (boolean) - optionally wrap the returned data in '<pre> tags
         * success_callback (function) - provide a custom success callback
         */
		ajax_submit: function(url, wrap_pre, success_callback, fancybox_opts) {
			$.fancybox.showLoading();
			
			var wrap_pre = wrap_pre || false;
			var fancybox_opts = fancybox_opts || {};
			
			if (!success_callback) {
				success_callback = function(data) {
    				$.fancybox.hideLoading();
    				data = wrap_pre ? '<pre>'+data+'</pre>' : data;
    				opts = {
    					'content': data,
    					'autoSize': false,
    					'width': '100%',
    					'height': '100%'   					
    				};
    				opts = _.extend(opts, fancybox_opts);
    				$.fancybox(opts);
    			}
			}
    		$.ajax({
    			type : "POST",
    			cache : false,
    			url : url,
    			data : $('#search_results_form').serializeArray(),
    			success: success_callback
    		});
		},
		
        /*
         * Function to export a list of selected papers or a query to ads classic
        */
		export_to_ads_classic: function() {
			this.remove_hidden();

			// if bibcodes are selected simply submit the form to the export url
			if (this.bibcodes_checked().length > 0) {
				this.disable_query_params();
				this.submit_form(GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL);
			// abstract view has only one bibcode
			} else if (this.is_abstract_page()) {
	        	var bibcode = $('#search_results_form').find('input[name="bibcode"]').val();
	        	this.add_hidden_field('bibcodes', bibcode)
				this.submit_form(GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL);
	        // pass a callback to the record count input selector along with a custom
	        // success callback that will insert the returned bibcodes (data) into the form
	        // before submitting to the export url
			} else {
				var RLM = this;
				this.enable_query_params();
				this.record_input_dialog('ADSClassic', function(numRecs) {
					RLM.ajax_submit(GlobalVariables.ADSABS2_GET_BIBCODES_ONLY_FROM_QUERY, false, function(data) {
						$.fancybox.hideLoading();
						RLM.disable_query_params();
						RLM.disable_sorting();
						RLM.add_hidden_field('bibcode', data);
						RLM.add_hidden_field('nr_to_return', numRecs);
						//submit the form
						RLM.submit_form(GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL);
//						$('#search_results_form').removeAttr('target').attr('action', GlobalVariables.ADS_CLASSIC_EXPORT_BASE_URL).submit();
					});
				});
			}
		},

        /*
         * Function to export a list of papers or a query in different formats
         */
        export_records_in_other_format: function(format) {

        	this.remove_hidden();
        	this.add_hidden_field('export_format', format);
        	if (this.bibcodes_checked().length > 0) {
        		this.disable_query_params();
        		this.ajax_submit(GlobalVariables.ADSABS2_EXPORT_TO_OTHER_FORTMATS_BASE_URL, true);
			} else if (this.is_abstract_page()) {
	        	var bibcode = $('#search_results_form').find('input[name="bibcode"]').val();
	        	this.add_hidden_field('bibcodes', bibcode);
        		this.ajax_submit(GlobalVariables.ADSABS2_EXPORT_TO_OTHER_FORTMATS_BASE_URL, true);
			} else {
				var RLM = this;
				this.enable_query_params();
				this.record_input_dialog('export_other', function(numRecs) {
					RLM.add_hidden_field('numRecs', numRecs);
					RLM.ajax_submit(GlobalVariables.ADSABS2_EXPORT_TO_OTHER_FORTMATS_BASE_URL, true);
				});
        	}
        },
        
        /*
         * load a visualization into fancybox
         */
        visualize: function(url, viz_type) {
        	this.remove_hidden();
        	this.enable_query_params();
        	if (this.bibcodes_checked().length > 0) {
        		this.ajax_submit(url);
        	} else {
				var RLM = this;
				this.record_input_dialog(viz_type, function(numRecs) {
					RLM.add_hidden_field('numRecs', numRecs);
					RLM.ajax_submit(url);
				});
        	}
        },
        
        /*
         * Function to get Citation Helper results
         */
        citation_helper: function() {
        	this.remove_hidden();
        	this.disable_query_params();
        	this.add_hidden_field('return_nr', 10)

        	var $inputs = (this.bibcodes_checked().length > 0)
        		? this.bibcodes_checked()
        		: this.bibcodes_displayed();

        	var checked = new Array();
        	$inputs.each(function() {
        		checked.push($(this).attr('value'));
        	});

        	var collapsed_bibcodes = checked.join('\n');
        	this.add_hidden_field('bibcodes', collapsed_bibcodes);
        	this.ajax_submit(GlobalVariables.ADSABS2_CITATION_HELPER_BASE_URL);
        },

        /*
        * Function to get Metrics results
        */        
        metrics: function() {
        	this.remove_hidden();
        	
        	if (this.bibcodes_checked().length > 0) {

        		this.disable_query_params();
        		var checked = new Array();
        		this.bibcodes_checked().each(function() {
        			checked.push($(this).attr('value'));
        		});
        		var collapsed_bibcodes = checked.join('\n');
        		this.add_hidden_field('bibcodes', collapsed_bibcodes);
        		this.ajax_submit(GlobalVariables.ADSABS2_METRICS_BASE_URL);

        	} else {
				var RLM = this;
        		this.enable_query_params();
				this.record_input_dialog('metrics', function(numRecs) {
					RLM.add_hidden_field('numRecs', numRecs);
					RLM.ajax_submit(GlobalVariables.ADSABS2_METRICS_BASE_URL);
				});
        	}        	
        },
        
        single_metrics: function() {
        	// this is some serious wtf how this works right now
        	var bibcode = $('#search_results_form').find('input[name="bibcode"]').val();
        	this.add_hidden_field('bibcodes', bibcode)
        	this.ajax_submit(GlobalVariables.ADSABS2_METRICS_BASE_URL);
        },
        
        export_to_libraries: function() {
            this.remove_hidden();
        	this.enable_query_params();
        	var url=GlobalVariables.ADS_PREFIX+'/adsgut/postform/ads/pub/html';
        	
        	if (this.bibcodes_checked().length > 0) {
        		this.ajax_submit(url, false, null, {'closeBtn': false});
        	} else {
        		var RLM = this;
        		this.record_input_dialog('export_library', function(numRecs) {
					RLM.add_hidden_field('numRecs', numRecs);
					RLM.ajax_submit(url, false, null, {'closeBtn': false});
        		})
        	}

        }
	}

}();

