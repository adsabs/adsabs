
	lib = {utility : {}};
	App = {};

lib.utility.fieldParse = function (field, str, logic)
	{	
		if (field === 'author')
			//we have to split on return rather than whitespace
			{	
					var args = str.split(/\r\n|\r|\n/g);
					var tempArgs = [];

					for (var i=0; i<args.length; i++)
					{
						if (args[i]!=="" && !/^\s+$/.test(args[i]) && args[i]!==null)
							{
								// trim() so extra whitespace at end of words is ignored
							tempArgs.push(args[i].trim())
							}
					}
					args = tempArgs;
					var tempArgs = []

					// and we need to put quotes around words, not +s and -s
					if (logic==='simple')
						// we need an extra parsing step
							{ for (var i=0; i< args.length; i++)
								{ 	parsed = args[i].match(/^\s*\+|^\s*\-/)||"" 
									parsed = parsed + ('"'+ args[i].match(/[\^?\w\s,]+/) +'"') 
									if (parsed !== '+"null"' && parsed !== '-"null"')
										{
											tempArgs.push(parsed)
										}
									else
										{
											tempArgs.push(parsed.charAt(0))
										}
								}
							}
					else //OR or AND-- just add quotes
							{for (var i=0; i< args.length; i++)
								{
									tempArgs.push(args[i]='"'+args[i]+'"')
								}
							}

				args = tempArgs
			}

		else if (field === 'bibstem')
			//split on commas
			{	var commaSplit = /\s*,\s*/
				args = str.split(commaSplit)
				var tempArgs = [];

				for (var i=0; i<args.length; i++)
				{
					if (args[i]!=="" && !/^\s+$/.test(args[i]) && args[i]!==null)
						{
							tempArgs.push(args[i])
						}
				}

				args = tempArgs;
			}
		else
			//split on quote-delimited phrases (with+ or - in front for simple logic), then whitespace
			{	var quoteSplit = /((\+|\-)?\"[^\"]+\")|(\+|\-)?\b\w+\b/g
				var args = str.match(quoteSplit);
			}
		return args
	},

lib.utility.fieldJoin = function(l, logic) { 
					if (l && l.length==1)
						{
							return l
						}

					else if (l)
							{if (logic ==='and')
								{
									var joined = l.join(' AND ');
								}
							else if (logic ==='or')
								{
									var joined = l.join(' OR ');
								}
							else if (logic==='simple')
								{
									var joined =l.join(',  ');
								}
							}

						return joined
					};

//autocomplete functions
lib.utility.split = function( val ) {
      return val.split( /,\s*/ );
    };

lib.utility.extractLast = function( term ) {
      return lib.utility.split( term ).pop();
    };


lib.utility.uniqueFormNames = function(selector, currentEl) {
	return _.uniq(currentEl.find(selector).map(function(){return $(this).attr("name")}).get());

}


//using: one model and two views (one for form and one for query/filter view)

//have to use nested plugin because we want the change event to register throughout the model
//for ui updating purposes

lib.formData = Backbone.NestedModel.extend({

	defaults : {
		filter: {
			database: ['astronomy'],
			date: {month_from:"", year_from:"", month_to:"", year_to:""},
			num_results: {items: 20},
			ref_filter: [],
		},
		query : {
			author: {args: "", logic:'and'} ,
			object: {args: "", logic:'and', simbad:false, ned: false, ads: false},
			title: {args: "", logic:'and' },
			abstract: {args: "", logic:'and'},
			bibstem: {args:"", logic: 'or'}
		}

	},

	initialize : function() {
		this.on("submit", this.submitData, this);
	},

	queryToString : function() { 
			query = "";
			var logicDict = {"and": " AND", "or": " OR", "boolean":"", "simple":", "};
			_.each(this.attributes.query, function(val, key) {
			if (val.args !== "" ){
				if (_.has(val, 'logic')) {
					//so that there aren't too many quotation marks

								query= query + key + ":(" + lib.utility.fieldParse(key, val.args, val.logic).join(logicDict[val.logic] +' ')+ ") "
						}
							
				else {
						query= query + key + ":(" + lib.utility.fieldParse(key, val.args, val.logic).join(',') + ") "
				}
			}
		})	
			return query;
	},

	submitData : function() {

		var queryString = this.queryToString();

 		var fullQueryObject = _.extend({'q' : queryString}, this.findFilters());

		var fullQuery = $.param(fullQueryObject)

		  if (fullQuery.length > 2000) {

		  	 //send in post request using a form
		  	 $("#classic_interact").append("<form id=\"workaround\" method=\"POST\" action=\""+GlobalVariables.SEARCH_BASE_URL+"\"></form>");

		  	 _.each(fullQueryObject, function(val, key){

		  	 	$("#workaround").append("<input name=\""+key+"\" value=\""+ val.toString().replace(/"/g, "&quot;") +"\" ></input>")
		  	 })


		  	// now add parameters to the form
		  	 $("#workaround").submit()
		}

		  else {
		  	 		window.location.href = GlobalVariables.SEARCH_BASE_URL + "?" + fullQuery
			}
	},

	findFilters : function()
		 	{   var that = this;
		 		var f = this.attributes.filter;
		 		var filters = {};

		 		//filter has to be there no matter what
		 		var dbf = [];
				_.each(f.database, function(x)
				{ 
						dbf.push(x)
				});	

		 		filters.db_f = "(" + dbf.join(' OR ')+ ")";

		 		_.each(f, function(val, key) {
		 			//adding facets only if they're not defaults!
		 			if (!_.isEqual(val, that.defaults.query[key])) 
		 				{

		 				if (key === 'ref_filter')
			 				{
			 					if (f.ref_filter.articles_only===true)
				 					{
				 						filters.article = 1
				 					}
			 				}
		 				else if (key === 'num_results')
			 				{
			 					filters.nr= f.num_results.items
			 				}
		 				else if (key === 'date')
			 				{
			 					for (x in f.date)
				 					{
				 						if (f.date[x]!=="")
				 						{
				 							filters[x] = f.date[x]
				 						}
				 					}
			 				}
		 			}
		 		});

		 		if (f.ref_filter.ref_only===true)
			 		{
			 			filters.prop_f = refereed
			 		};

		 		return filters
		 	}
}),


lib.formDataView = Backbone.View.extend({

	el : "#classic_container",

	events : {"click #search_submit" : "transmitData",
				"click #clear" : "resetForm",
				"keyup input[type=\"text\"], textarea": "updateModel",
				//added the blur, which catches changes when someone held down a key for a long time (this will never happen in real life but w/e)
				"blur input[type=\"text\"], textarea": "updateModel",
				// we dont want to call change event for text or textarea, since we are already capturing keyup
				"change input[type=\"checkbox\"], input[type=\"radio\"]" : "updateModel"
			},


	initializeForm : function(){

		infoOnBackButton  = $("#json-data").val();

		if (infoOnBackButton) {
			startData = JSON.parse(infoOnBackButton);
			this.model.set(startData);

			//finally, trigger model change event
			this.model.trigger("change");
		}

	},

	resetForm : function (){
		this.model.clear().set(this.model.defaults);

		var that = this;
		//reset textareas and text inputs, easy
		this.$el.find("textarea").val("");
		this.$el.find("input[type=text]").val("");
		// less easy-get names of radio and checkbox groups
		var radioGroups = lib.utility.uniqueFormNames("input[type=\"radio\"]", that.$el); 
		var checkboxGroups = lib.utility.uniqueFormNames("input[type=\"checkbox\"]", that.$el);

		_.each(radioGroups, function(t){
			var model_id = t.replace(/-/g, ".").trim();
			var resetVal = that.model.get(model_id);
			$('input[value="'+resetVal+'"]').prop('checked', true);

		});

		_.each(checkboxGroups, function(n){
			var model_id = n.replace("-", ".").trim();
			var resetVals = that.model.get(model_id)
			$('input[name='+n+']').each( function(){

				if (_.contains(resetVals,$(this).val()))
					{	
						$(this).prop("checked", true)
					}
				else {	
						$(this).prop("checked", false)
					}
				});
			});
	},

	transmitData : function() {

		//first, update the hidden field so it is available on a possible back navigate
		$("#json-data").val(JSON.stringify(this.model.toJSON()))
		this.model.trigger("submit")
	},

	updateModel : function(e){
		var eel = e.target;
		if ($(eel).attr("type")==="checkbox") {
				var n = $(eel).attr("name");
				var model_id = n.replace(/-/g, ".").trim();
				// create list from checked boxes
				var vals = [];
				$("input[name="+ n +"]:checked").each(function(){
						vals.push($(this).val())
					})
				this.model.set(model_id, vals)

			}
		else {
			var newVal = $(eel).val();
			var n = $(eel).attr("name");
			var model_id = n.replace(/-/g, ".").trim();
			this.model.set(model_id, newVal)

		}
	}
})


lib.queryDisplayView = Backbone.View.extend({

	el : "#classic_container",

	initialize : function() {
		this.listenTo(this.model, 'change:filter', this.filterConvert)
		this.listenTo(this.model, 'change:query', this.queryBarConvert)
	},

	events : {"click #classic_q" : "preventEdit",
			  "keyup #classic_q" :"preventEdit",
			  "keydown #classic_q" : "preventEdit"},

	preventEdit : function (e) {	
		var q = $(e.target);
			q.prop("disabled", true);
			setTimeout(function(){q.prop("disabled", false)},5000);
		},

	queryBar : [],

	queryBarConvert : function() {
		this.queryBar = [];
		var that = this;
		_.each(this.model.attributes.query, function(val, key, list){
			// only displaying if there are args and it is different from default
			if (!_.isEqual(val, that.model.defaults.query[key]) && val["args"]) {

				//take care of bibstem special case, which only has 'or' logic
				if (key=='bibstem') {
					var args =  lib.utility.fieldParse('bibstem',that.model.attributes.query.bibstem.args, 'or');
					that.queryBar.push('bibstem:(' + lib.utility.fieldJoin(args, 'or') + ')');
					return
				};

				var logic = that.model.attributes.query[key]['logic']
				// if logic is boolean, the user has already formatted the query, so just attach it to queryBar
				if (logic === 'boolean') {
					var args = that.model.attributes.query[key]["args"];
						that.queryBar.push(key+ ':('+args+')');
						return
					}

				var args = lib.utility.fieldParse(key, that.model.attributes.query[key].args, logic);
				var args = lib.utility.fieldJoin(args, logic)
				that.queryBar.push(key+ ':('+args+')')
			}
		});
		var queryView = this.queryBar.join(" ");

		this.$el.find('#classic_q').val(queryView);

	},

	filterConvert : function(){

		var that = this;
		this.$el.find('#classic_filter_div').empty();

		_.each(this.model.attributes.filter, function(val, key, list){

				// we have a filter val that has changed, so clear the div

				if (key ==="date" && !(val.month_from === "" 
								&& val.year_from === ""
							 	&& val.month_to === "" && val.year_to ==="")) {

						var start = [];
								var end = [];
								start.push(val.month_from);
								start.push(val.year_from);
								end.push(val.month_to);
								end.push(val.year_to);

								var s = (JSON.stringify(start) != JSON.stringify(["",""]) ? start.join('/') : '');
								var e = (JSON.stringify(end) != JSON.stringify(["",""]) ? end.join('/') : '');

								var s = s.replace(/^\//g, '');
								var e = e.replace(/^\//g, '');

								if (e)
								{
									var totalDate = s + '-'+ e
								}
								else
								{
									var totalDate = s
								}
								
								var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Date: ' + totalDate + '</span>');
									that.$el.find('#classic_filter_div').append(new_filter);
									that.$el.find('#classic_filter_div').append('<br/>');
					}

				else if (key === "num_results") {

							if (val.items !=="")

								{
									var num = val.items;
								}
								else
								{
									var num = 20;
								}
								var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Results per page: ' + num + '</span>');
									that.$el.find('#classic_filter_div').append(new_filter);
									that.$el.find('#classic_filter_div').append('<br/>');
							}

				else if (key ==="ref_filter")
							{
								if (_.contains(val, 'ref_only')) 
									{
									var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Refereed only </span>');
									that.$el.find('#classic_filter_div').append(new_filter);
									that.$el.find('#classic_filter_div').append('<br/>');
									}
								else  
								{
									var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Refereed <span style="font-variant:small-caps"> or </span> Non-refereed</span>');
									that.$el.find('#classic_filter_div').append(new_filter);
									that.$el.find('#classic_filter_div').append('<br/>');
								}

								if (_.contains(val, 'articles_only'))
								{
									var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Articles only</span>');
									that.$el.find('#classic_filter_div').append(new_filter);
									that.$el.find('#classic_filter_div').append('<br/>'); 
								}

							}

				else if (key === 'database') {
						
							if (_.contains(val, 'physics') && !_.contains(val, 'astronomy'))
							{
								var new_filter = $('<span class="classicAppliedFilter">'
								+ 'Database: Physics' + '</span>');
							}
							else if (_.contains(val, 'physics') && _.contains(val, 'astronomy'))
							{ 
							 	var new_filter = $('<span class="classicAppliedFilter">'
								+ 'Database: '+ ' Astro <span style="font-variant:small-caps">or</span> Physics' + '</span>');
							}
							else if (!_.contains(val,'physics') && _.contains(val, 'astronomy'))
							{
								 var new_filter = $('<span class="classicAppliedFilter">'
								+ 'Database: Astronomy' + '</span>');
							}

							that.$el.find('#classic_filter_div').append(new_filter);
							that.$el.find('#classic_filter_div').append('<br/>');							
						}
		})
	},

});

//autocomplete
App.initiatePubAutocomplete = function () {
	$("textarea[name=query-bibstem-args]").bind( "keydown", function( event ) {
	if ( event.keyCode === $.ui.keyCode.TAB &&
	    $( this ).data( "ui-autocomplete" ).menu.active ) {
	  event.preventDefault();
		}
	})
	.autocomplete({
		source: function( request, response ) {
			$.getJSON( GlobalVariables.AUTOCOMPLETE_BASE_URL + "pub", {
		    term: lib.utility.extractLast( request.term )
		  }, response );
		},
		search: function() {
		  // custom minLength
		  var term = lib.utility.extractLast( this.value );
		  if ( term.length < 2 ) {
		    return false;
		  }
		},
		focus: function() {
		  // prevent value inserted on focus
		  return false;
		},
		select: function( event, ui ) {
		  var terms = lib.utility.split( this.value );
		  // remove the current input
		  terms.pop();
		  // add the selected item
		  terms.push( ui.item.value );
		  // add placeholder to get the comma-and-space at the end
		  terms.push( "" );
		  this.value = terms.join( ", " );
		  // added this to make query bar at top work
		  $("textarea[name=query-bibstem-args]").val(terms.join( ", " ))
		  $("textarea[name=query-bibstem-args]").trigger('click')
		  return false;
		}
	})
};


$(document).ready(function(){

	App.formData = new lib.formData();
	App.formDataView = new lib.formDataView({model : App.formData});
	App.queryDisplayView = new lib.queryDisplayView({model : App.formData});

	App.initiatePubAutocomplete();
	App.formDataView.initializeForm();


})
