
// module name is "classicSearch"

classicSearch = {};

//utility functions

//takes a string, returns a list of split tokens that have quotation marks correctly inserted
classicSearch.fieldParse = function (field, str, searchObject)
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
					{	if (searchObject['author']['logic']==='simple')
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
	}

// joins split tokens based on logic
classicSearch.fieldJoin = function(l, logic)
	{ 
		if (l.length==1)
		{
			return l
		}

		else
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
					var joined =l.join(' ');
				}
			}

		return joined
	}


//this function takes a classicSearch.searchObject and returns a string that represents a proper solr query
classicSearch.convertSearchObjectToDisplayQuery = function (searchObject)
	{	var solrQuery = [];
		var textAreas = ['author', 'object', 'title', 'abstract'];

		for (key in searchObject) 
			{	///we only care if it doesn't match the default
				//we need to compare string representations since there is no easy way
				//to check for object equivalence in javascript
				if (searchObject[key]["args"]!= [])
					{
						var d = searchObject[key];
						//cycling through textAreas
						for (var i=0; i<textAreas.length; i++)
							{
								if (key ===textAreas[i])
									
									{ 
										var args = d['args'];

										if (d['logic']==='boolean')
											//the user has already formulated the query
											//for you and it can be added as-is
											{
												solrQuery.push(key+ ':('+args+')')
												break
											}

										else {	

												args = classicSearch.fieldParse(textAreas[i], args, searchObject)
												args = classicSearch.fieldJoin(args, d['logic'] )
												//if author field and "require author for selection", we need to put a 
												// plus sign in front of the field itself
												if (d['require']===true)
													{	
														solrQuery.push('+'+key+ ':('+args+')')
														break
													}
												else
													{
														solrQuery.push(key+ ':('+args+')')
														break
													}
											}
									}			
							}
					}
			}

		//now dealing with bibstem special case
		if (searchObject["bibstem"]["args"]!="")

			{
				var args =  classicSearch.fieldParse('bibstem', searchObject["bibstem"]["args"]);
				solrQuery.push('bibstem:(' + classicSearch.fieldJoin(args, 'or') + ')')
			}

		return solrQuery.join(" ")

	}

classicSearch.convertSearchObjectToDisplayFilters = function (searchObject) 
		{
			var otherAreas = ['date', 'num_results', 'ref_filter', 'Database'];
			$('#classic_filter_div').empty();

			for (key in searchObject) 
				{	
							if (key ==="date" && !(searchObject["date"]["month_from"] === "" 
								&& searchObject["date"]["year_from"] === ""
							 	&& searchObject["date"]["month_to"] === "" && searchObject["date"]["year_to"] ===""))
							{ 	var d = searchObject["date"]
								//turn into two lists
								var start = [];
								var end = [];
								start.push(d['month_from']);
								start.push(d['year_from']);
								end.push(d['month_to']);
								end.push(d['year_to']);

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
									$('#classic_filter_div').append(new_filter);
									$('#classic_filter_div').append('<br/>');
							}
							else if (key ==="num_results")
							{	if (searchObject['num_results']['items']!=="")

								{
									var num = searchObject[key]['items'];
								}
								else
								{
									var num = 20;
								}
								var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Number of results: ' + num + '</span>');
									$('#classic_filter_div').append(new_filter);
									$('#classic_filter_div').append('<br/>');
							}
							else if (key ==="ref_filter")
							{	
								if (searchObject['ref_filter']['ref_only']===true) 
									{
									var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Refereed only </span>');
									$('#classic_filter_div').append(new_filter);
									$('#classic_filter_div').append('<br/>');
									}
								else  
								{
									var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Refereed <span style="font-variant:small-caps"> or </span> Non-refereed</span>');
									$('#classic_filter_div').append(new_filter);
									$('#classic_filter_div').append('<br/>');
								}

								if (searchObject['ref_filter']['articles_only']===true)
								{
									var new_filter = $('<span class="classicAppliedFilter">'
									+ 'Articles only</span>');
									$('#classic_filter_div').append(new_filter);
									$('#classic_filter_div').append('<br/>'); 
								}

							}
						
							else if (key ==="Database")
									{	
										var d = searchObject[key];
										if (d['physics']===true && d['astronomy']===false)
										{
											var new_filter = $('<span class="classicAppliedFilter">'
											+ 'Database: Physics' + '</span>');
										}
										else if (d['physics']===true && d['astronomy']===true)
										{
										 	var new_filter = $('<span class="classicAppliedFilter">'
											+ 'Database: '+ ' Astro <span style="font-variant:small-caps">or</span> Physics' + '</span>');
										}
										else if (d['physics']===false && d['astronomy']===true)
										{
											 var new_filter = $('<span class="classicAppliedFilter">'
											+ 'Database: Astronomy' + '</span>');
										}

										$('#classic_filter_div').append(new_filter);
										$('#classic_filter_div').append('<br/>');
							}
				}				
		}

//big event function--using closure to hide classicSearch.searchObject
//note--we have to listen to two different events: "change" as well as "keyup"
//we alter the search object and from that the display query upon detection of either of these events

classicSearch.classicFormFunction = function(){

	var searchBar = $('#classic_q');
	//filter is false until someone presses the button
	var filter = false;

	var formInteract = function() {

		// this function reacts to a change in the form and updates the classicSearch.searchObject object
		// to reflect that change. It then updates the query bar at the top. Note--only the event target is used to update the classicSearch.searchObject
		// after every event, it doesn't look everywhere to redo the entire classicSearch.searchObject.
		// For onChange, ultimately parental OR grandparental id is what we use to figure out the entry in classicSearch.searchObject that
		// needs to be updated, so the id of the grandparent or great-grandparent or great-great-grandparent (var f) for all checkbox and radio form controls needs to 
		// have an id that matches a search object field. (If grandparent, or further down the line then the parent itself cannot have an id or it won't work)

	function onChange (evt)	
			{ 	

				//the element that was changed
				var target = $(evt.target);
				var type = target.attr('type')	

				// it's a checkbox or radio field
				if (type === "checkbox" || type === "radio")

					{	var isChecked = target.prop('checked')
						//sometimes its the grandparent, sometimes the great-grandparent or great-great-grandparent
						var f = target.parents().eq(1).attr('id') || target.parents().eq(2).attr('id') || target.parents().eq(3).attr('id');
						var name = target.attr("name")

					if (f=="ref_filter")
						{	
							var id= target.attr("id");
							classicSearch.searchObject[f][id]=isChecked;		
						}
					
					else if (f === "Database")
						{  
							var id= target.attr("id");
							classicSearch.searchObject[f][id]=isChecked
						}

					else
						//it's an author, object, title, or abstract field
						{
							var c= target.attr("class")
							// it's a logic radio
							if (name !== undefined && name.indexOf("logic")!==-1)
								{	
									classicSearch.searchObject[f]['logic']=c
								}
						}
					}

				// it's an input field
				else 
				{			
							// for bibstem, this is in grandparent
							var f = target.parent().attr('id') || target.parents().eq(1).attr('id');
							var type = target.attr("type");

					if (['author', 'object', 'title', 'bibstem', 'abstract'].indexOf(f)!==-1) 
						// it's a textarea
						{
							classicSearch.searchObject[f]['args']= target.val();
						}	
					// else, it's a filter 
						else  {
							if (f === "date")
								{
								    i = target.index();
								    if (i === 0)
								    {
								    	classicSearch.searchObject[f]['month_from'] = target.val()
								    }
								    else if (i===1)
								    {
								    	classicSearch.searchObject[f]['year_from'] = target.val()
								    }
								    else if (i===2)
								    {
								    	classicSearch.searchObject[f]['month_to'] = target.val()
								    }
								    else if (i===3)
								    {
								    	classicSearch.searchObject[f]['year_to'] = target.val()
								    }
								}

							else if (f === "num_results")
							 		{	
								    	classicSearch.searchObject["num_results"]['items'] = target.val()
								    }

						} //end filter augment

				}
			//this takes care of search bar
			var newQuery = classicSearch.convertSearchObjectToDisplayQuery(classicSearch.searchObject);
				searchBar.val(newQuery);

			//this takes care of filter arguments
			classicSearch.convertSearchObjectToDisplayFilters (classicSearch.searchObject);

			}// end onChange 

		// applying onChange to all relevant events
		$("#classic_interact").on(
			{
				keyup:  function(evt) {onChange(evt)}
			}
		)
		// do not apply this to the entire #classic_form or click events anywhere
		// will have unforeseen events!
		$("#classic_interact input, #classic_interact textarea").on(
			{
				click: function(evt) {onChange(evt)}
			}
		)

		// // clearing the form upon back button usage
		// $(window).bind("pageshow", function() {
  //   			var form = $('#classic_form'); 
  //   			// let the browser natively reset defaults
  //   			form[0].reset();
		// });


		//finally, the function that converts searchObject entries to url parameters

		classicSearch.findFilters = function()
		 	{
		 		var otherAreas = ['date', 'num_results', 'ref_filter', 'Database']
		 		var filters = []

		 		//filter has to be there no matter what
		 		var dbf = [];
				for (x in classicSearch.searchObject['Database'])
				{
					if (classicSearch.searchObject['Database'][x] === true)
					{
						dbf.push(x)
					}
				}					
		 		filters.push('db_f=%28'+ encodeURIComponent(dbf.join(' OR '))+'%29')

		 		for (var i=0; i< otherAreas.length; i++)
		 		{
		 			//adding facets only if they're not defaults!
		 			if (JSON.stringify(classicSearch.searchObject[otherAreas[i]])!==JSON.stringify(classicSearch.defaultSearchObject[otherAreas[i]]))
		 			{
		 				if (otherAreas[i]==='ref_filter')
			 				{
			 					if (classicSearch.searchObject['ref_filter']['articles_only']===true)
				 					{
				 						filters.push("article=1")
				 					}

			 				}
		 				else if (otherAreas[i]==='num_results')
			 				{
			 					filters.push("nr="+encodeURIComponent(classicSearch.searchObject[otherAreas[i]]["items"]))
			 				}
		 				else if (otherAreas[i]==='date')
			 				{
			 					for (x in classicSearch.searchObject['date'])
				 					{
				 						if (classicSearch.searchObject['date'][x]!=="")
				 						{
				 							filters.push(x+'='+encodeURIComponent(classicSearch.searchObject['date'][x]))
				 						}
				 					}
			 				}
		 			}
		 		};

		 		if (classicSearch.searchObject['ref_filter']['ref_only']===true)
			 		{
			 			filters.push("prop_f=refereed")
			 		};

		 		return filters
		 	}

	$('#search_submit').on("click", function(e) {
		e.preventDefault(); 
 		var query = $("#classic_q").val();
 		var filters = classicSearch.findFilters() || "";
 		// in case someone marks a month
 		if ((filters.join('').match(/month_from/) && !filters.join('').match(/year_from/)) || (filters.join('').match(/month_to/) && !filters.join('').match(/year_to/)) )
 			{
 				$(".classic_container").prepend("<div class=\"alert alert-error\" style=\"width:82%\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button><strong>Error!</strong> Month field designated without a corresponding year!</div>")
 			}
 		else 
 			{
 				window.location.href = 'http://labs.adsabs.harvard.edu/adsabs/search/?q='+encodeURIComponent(query) +'&' + filters.join('&')
 			}
 	})
			
			
	} // end formInteract

	return formInteract

} // end  classicFormFunction

classicSearch.searchObject = {
		Database: {'astronomy':true, 'physics': false},
		author: {args: "", logic:'and'} ,
		object: {args: "", logic:'and', simbad:false, ned: false, ads: false},
		date: {month_from:"", year_from:"", month_to:"", year_to:""},
		title: {args: "", logic:'and' },
		abstract: {args: "", logic:'and'},
		num_results: {items: 20},
		ref_filter: {ref_only: true, articles_only: false},
		bibstem: {args:""},
	};

classicSearch.defaultSearchObject = {
		Database: {'astronomy':true, 'physics': false},
		author: {args: "", logic:'and'} ,
		object: {args: "", logic:'and', simbad:false, ned: false, ads: false},
		date: {month_from:"", year_from:"", month_to:"", year_to:""},
		title: {args: "", logic:'and' },
		abstract: {args: "", logic:'and'},
		num_results: {items: 20},
		ref_filter: {ref_only: true, articles_only: false},
		bibstem: {args:""},
	}; 



classicSearch.preventEdit = function (e)
	{	var $i = $("#classic_q");
		$i.prop("disabled", true);
		setTimeout(function(){$i.prop("disabled", false)},3000);


	}

classicSearch.tooltipToggle = function() {
        var $t = $(this);
        $t.toggleClass("help_activated");
 
        if ($t.hasClass("help_activated"))
            {
                $t.css({'background-color':'#C1F5D7', 
                    'box-shadow': 'none'});
                $("#classic_entire_filter_div").animate({'margin-top':'5px'}, 1500)
                $("#classic_help_explanation").show(1500);
 
                $("#classic_form div").each(function()
                    {
                        var $this = $(this);
                        var title = $this.data('hidden_title');
                        $this.attr('data-original-title', title);
                    }
                )
 
                $("#classic_form div").tooltip({'placement':'top'});    
            }
 
        else 
            {
                $t.css({'background-color':'white',
                    'box-shadow': ''});
                $("#classic_help_explanation").hide(1500);
                $("#classic_entire_filter_div").animate({'margin-top':'140px'}, 1500);
                $("#classic_form div").each(function()
                    {
                        var $this = $(this);
                        $this.data('hidden_title', $this.attr('data-original-title'));
                        $this.removeAttr('data-original-title');
                        $this.removeAttr('title');
                    }
                )
 
 
            }
    }

classicSearch.pageInitiate = function ($item)	
		{ 	

			//the element that was changed
			var target = $item;
			var type = target.attr('type')	

			// it's a checkbox or radio field
			if (type === "checkbox" || type === "radio")

				{	var isChecked = target.prop('checked')
					//sometimes its the grandparent, sometimes the great-grandparent or great-great-grandparent
					var f = target.parents().eq(1).attr('id') || target.parents().eq(2).attr('id') || target.parents().eq(3).attr('id');
					var name = target.attr("name")

				if (f=="ref_filter")
					{	
						var id= target.attr("id");
						classicSearch.searchObject[f][id]=isChecked;		
					}
				
				else if (f === "Database")
					{  
						var id= target.attr("id");
						classicSearch.searchObject[f][id]=isChecked
					}

				else
					//it's an author, object, title, or abstract field
					{
						var c= target.attr("class")
						// it's a logic radio
						if (name !== undefined && name.indexOf("logic")!==-1)
							{	
								classicSearch.searchObject[f]['logic']=c
							}
					}
				}

			// it's an input field
			else 
			{			
						// for bibstem, this is in grandparent
						var f = target.parent().attr('id') || target.parents().eq(1).attr('id');
						var type = target.attr("type");

				if (['author', 'object', 'title', 'bibstem', 'abstract'].indexOf(f)!==-1) 
					// it's a textarea
					{
						classicSearch.searchObject[f]['args']= target.val();
					}	
				// else, it's a filter 
					else  {
						if (f === "date")
							{
							    i = target.index();
							    if (i === 0)
							    {
							    	classicSearch.searchObject[f]['month_from'] = target.val()
							    }
							    else if (i===1)
							    {
							    	classicSearch.searchObject[f]['year_from'] = target.val()
							    }
							    else if (i===2)
							    {
							    	classicSearch.searchObject[f]['month_to'] = target.val()
							    }
							    else if (i===3)
							    {
							    	classicSearch.searchObject[f]['year_to'] = target.val()
							    }
							}

						else if (f === "num_results")
						 		{	
							    	classicSearch.searchObject["num_results"]['items'] = target.val()
							    }

					} //end filter augment

			}

		}// end pageInitiate


//autocomplete functions
classicSearch.split = function( val ) {
      return val.split( /,\s*/ );
    }

classicSearch.extractLast = function( term ) {
      return classicSearch.split( term ).pop();
    }

//autocomplete
classicSearch.initiatePubAutocomplete = function () {
	$("#pubtext").bind( "keydown", function( event ) {
	if ( event.keyCode === $.ui.keyCode.TAB &&
	    $( this ).data( "ui-autocomplete" ).menu.active ) {
	  event.preventDefault();
		}
	})
	.autocomplete({
		source: function( request, response ) {
			$.getJSON( GlobalVariables.AUTOCOMPLETE_BASE_URL + "pub", {
		    term: classicSearch.extractLast( request.term )
		  }, response );
		},
		search: function() {
		  // custom minLength
		  var term = classicSearch.extractLast( this.value );
		  if ( term.length < 2 ) {
		    return false;
		  }
		},
		focus: function() {
		  // prevent value inserted on focus
		  return false;
		},
		select: function( event, ui ) {
		  var terms = classicSearch.split( this.value );
		  // remove the current input
		  terms.pop();
		  // add the selected item
		  terms.push( ui.item.value );
		  // add placeholder to get the comma-and-space at the end
		  terms.push( "" );
		  this.value = terms.join( ", " );
		  // added this to make query bar at top work
		  $('#pubtext').val(terms.join( ", " ))
		  $('#pubtext').trigger('click')
		  return false;
		}
	});
}