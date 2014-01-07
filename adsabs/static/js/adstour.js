
$(document).ready( function() {	
	
	var currentPath = new Uri(window.location.href).path();
	adsTour.init(currentPath);

});

var adsTour = function() {
	return {

		
		flash: function(sel) {
			$(sel).animate( { color: 'rgb(255,0,0)' }, 200 );
			$(sel).animate( { color: "black" }, 1000 );
		},
		
		appendToQ: function(s) {
			$("input#q").val(s);
			this.flash("input#q")
		},
		
		removeFromQ: function() {
			$("input#q").val('');
		},

		makeTour: function(currentPath) {
			this.tour= new Tour({backdrop:false, storage:false});

			var tourPath = _.find(_.keys(tourSteps), function(pathKey) {
				pathKey = GlobalVariables.ADS_PREFIX + pathKey;
				return currentPath.match(new RegExp(pathKey, "i"))
			});

			if (tourPath == undefined) return;
			var addStepsFunc = tourSteps[tourPath];
			addStepsFunc(this);
			this.tour.init();
			this.tour.start();
			},

		init : function(currentPath) {
				$("#tour").show().on("click", function(e) {
				adsTour.makeTour(currentPath);
				e.preventDefault();					
			})}
	};
}();

var tourSteps = {
	"^\/$": function(adsTour) {
		//store the search variable if there is one
		var currentSearch = $("#q").val();

		adsTour.tour.addSteps([
		  {
		    element: "li#tour", 
		    title: "Welcome to the ADS Main Search Page", 
		    content: "This tour will show you how to quickly write a targeted ADS query.",
		    placement:'right'
		  },
		  	{
		    element: "i.icon-user", 
		    title: "Sign In for More Options", 
		    content: "You can always log in with your ADS credentials to personalize your search experience.",
		    placement:'left'
			},

		  {
		    element: "a:contains('Search the ADS')", 
		    title: "Compose Your Query", 
		    content: "Our new one-box query form uses both fielded and unfielded search for a speedy, powerful search."
		  },
		  {
		    element: "#classic-search-tab", 
		    title: "Classic Search", 
		    content: "(You can click over to the classic search form if you'd like a more structured search experience.)"
		  },
		  {
		    element: "#q", 
		    title: "Unfielded Search", 
		    content: "This is an example of an unfielded search you could use. It is simple to type, but the search results might be too broad.",
		    onShown: function(tour) {adsTour.appendToQ("redshift fizeau 1848")},
		    placement:'right'
		  },

		  {
		    element: "#q", 
		    title: "Fielded Search", 
		    content: "This is an example of fielded search. It will yield a more precise set of results.",
		    onShown: function(tour) {adsTour.appendToQ("title:\"redshift\" author:\"fizeau\" year:1848")},
		    placement:'right'
		  },

		   {
		    element: "a.link_only_js:eq(0)", 
		    title: "Author Search", 
		    content: "Type author names in the form <br/>\"last, first middle initial\", and separate them with semicolons.",
		    placement:'top',
		    onShown: function(tour) {adsTour.appendToQ("author:\"huchra, j; macri, l; masters, k\"")}
		  },
		  	{
		    element: "a.link_only_js:eq(1)",
		    title: "First Author Search", 
		    content: "Similar to the author search, but this will only search for the names in the first author slot of each publication.",
		    placement:'top',
		    onShown: function(tour) {adsTour.appendToQ("author:\"^huchra, j\"")}
		  },
		  	{
		    element: "a.link_only_js:eq(2)", 
		    title: "Title Search", 
		    content: "If you have a word or phrase that should appear in the title of a work, use this operator. ",
		    placement:'top',
		    onShown: function(tour) {adsTour.appendToQ("title:\"QSO\"")}
		  },
		  	{
		    element: "a.link_only_js:eq(3)",
		    title: "Year Search", 
		    content: "Date Format: YYYY or YYYY-YYYY",
		    placement:'top',
		    onShown: function(tour) {adsTour.appendToQ("year:1995-2000")}
		  },

		  	{
		    element: "a.link_only_js:eq(4)", 
		    title: "Publication Search", 
		    placement:'top',
		    content: "Use journal abbreviations from our <a target=\"_blank\" href=\"http://adsabs.harvard.edu/abs_doc/journal_abbr.html\">bibstem list.</a>",
		    onShown: function(tour) {adsTour.appendToQ("bibstem:\"ApJ, MNRAS\"")}
		  },
		  	{
		    element: "a.link_only_js:eq(5)",
		    title: "Full Text Search", 
		    content: "This operator performs an expansive search into the actual text of articles as well as various fields such as date, publication, and author.",
		    placement:'top',
		    onShown: function(tour) {adsTour.appendToQ("full:\"alien life forms\"")}
		  },
		  	{
		    element: "a.link_only_js:eq(2)",
		    title: "More Complex Queries with Parentheses", 
		    content: "You can use parentheses with search operators for more complex boolean queries.",
		    placement:'top',
		    onShown: function(tour) {adsTour.appendToQ("title:((exoplanets or \"extrasolar planets\") and kepler)")}
		  },
		  {
		    element: "#tour-anchor-advanced-operators", 
		    title: "Advanced Search Operators", 
		    content: "These three operators wrap a finished query and give you new insight into your target area of study."
		    		+ " For instance, the query currently in the search bar will return a ranked list of papers which are"
		    		+ " popular right now among the readers interested in exoplanets.",
		    placement:'bottom',
		    onShown: function(tour) {adsTour.appendToQ("trending(exoplanets)")}
		  },

		  {
		  	element: "#tour-anchor-advanced-operators",
		    title: "Advanced Search Operators", 
		    content: "For a closer look at all three operators, mouse over one of the three links to read a short explanation.", 
		    placement:'bottom',
		    onShown: function(tour) {adsTour.appendToQ(currentSearch)},
		  },

		  {
		    element: "span#drawer_handler", 
		    title: "Advanced Options", 
		    content: "Click here to find filters that will help you obtain a more targeted"
		    + " set of search results.",
		    placement:'top',
		    onShown: function(tour) {$("#drawer_handler").trigger("click")},
		    onNext:function(tour) {$("#drawer_handler").trigger("click")}
		  },

		  {
		    element: "#feedback_widget", 
		    title: "Thank You!", 
		    content: "Thank you for taking the tour of the ADS main page. If you have any questions or comments, click here to let us know!",
		    placement:'right'
		  }
		]);		
	},
	"^/search/$": function(adsTour) {
		adsTour.tour.addSteps([
				{
			    element: "li#tour", 
			    title: "Welcome to the ADS Search Results Page", 
			    content: "For best results with the tour, make sure you are showing multiple results from a fairly broad search term (e.g, \"exoplanets\"), and that you have not yet clicked anything on the page.",
			    placement:'right'
			  },
			  {
			    element: "div.accordion-toggle.facetAccordionHeader", 
			    title: "Filter Your Search Results", 
			    content: "This column gives you many ways to narrow your results.",
			    placement:'right'
			  },
			  	{
			    element: "div.accordion-toggle:eq(2)", 
			    title: "authors", 
			    content: "If you search for an author named \"Zhang, Z\", for instance, your search might turn up results from many different individuals. A quick way to target a specific author or to exclude other authors with similar names is to click on the <i class=\"icon-chevron-right\"></i> symbol to open up a list of names that have been grouped under this name.",
			    onShown: function(tour) {setTimeout(function(){$(".expCollSubFacetaut_f:eq(0)").trigger("click")}, 2000)},
			    placement:'right'
			   },
			   	{
			    element: "div.accordion-inner:eq(1)", 
			    title: "Limit Results to Specific Authors", 
			    content: "To limit your search to a certain author name, click on the name. To exclude an author name from your results, check the box next to the name, navigate to the \"apply\" button, and hit \"exclude\".",
			    onNext:function(tour) {$(".expCollSubFacetaut_f:eq(0)").trigger("click")},
			    placement:'right'
			   },
			  {
			    element: "div.accordion-toggle:eq(6)", 
			    title: "Limit Results to Refereed Publications", 
			    content: "If your search yields both refereed and non-refereed items, and you only wish to view refereed articles, you could click on the \"refereed\" link to instantly be taken to a narrowed set of results.",
			    placement:'right',
			    onShown: function(tour) {
			    	$("div.accordion-toggle:eq(6)").removeClass("collapsed"); 
			    	$("#collapserefereed_f").toggleClass("in");
			    	} 
			   },
			   	{
			    element: "div.accordion-toggle:eq(11)", 
			    title: "Limit Date Range", 
			    content: "Or you could filter your results based on a specified year range by changing the positions of the slider toggles or entering in a year range.",
			    placement:'right'
				},
				{
			    element: "div.row-fluid.searchresult:eq(0) a:eq(0)", 
			    title: "Go to Individual Article View", 
			    content: "Clicking on the bibcode or title of an individual article will bring you to a page showing the abstract view for that article.",
			    placement:'top'
				},
				{
			    element: "div.row-fluid.searchresult:eq(0) input[type=checkbox]", 
			    title: "Select an Article for Aggregate Analysis", 
			    content: "This page provides many options for analyzing the content or metadata of a group of search results. To select one or more articles for analysis, click the checkbox next to the article.",
			    placement:'left',
			    onShown: function(tour) {$("div.row-fluid.searchresult:eq(0) input[type=checkbox]").trigger("click")},
			    onNext:function(tour) {$("div.row-fluid.searchresult:eq(0) input[type=checkbox]").trigger("click")}
				},

				{
			    element: "div.row-fluid.well.well-small span.btn:eq(0)", 
			    title: "Select all Articles on this Page for Aggregate Analysis", 
			    content: "To select all articles on the current page for analysis, click this button.",
			    placement:'top',
			    onShown: function(tour) {setTimeout(function(){$("i.icon.icon-check").parent().trigger("click")},1500)},
			    onNext:function(tour) {$("i.icon.icon-check").parent().trigger("click")}
				},
				{ element: "div.row-fluid.well.well-small div.span7.pull-right", 
			    title: "Default Settings for Aggregate Analysis", 
			    content: "If you do not select any articles for analysis, you will be offered the choice to limit your analyzed result set upon choosing your analysis or export method. We will look at different analysis and export options now.",
			    placement:'left'
				},
				{
			    element: "a.btn.dropdown-toggle:contains(Analyze)", 
			    title: "Analyze Your Results", 
			    content: "This button provides a citation helper, which lists articles that have cited or have been cited in your currently selected articles. The metrics view shows a comprehensive set of metrics for currently selected articles.",
			    placement:'top',
			   	onShown: function(tour) {setTimeout(function(){$("a.btn.dropdown-toggle:contains(Analyze)").trigger("click")},1000)},
			    onNext:function(tour) {$("a.btn.dropdown-toggle:contains(Analyze)").trigger("click")}
				},
				{
			    element: "a.btn.dropdown-toggle:contains(View)", 
			    title: "Visualize Your Results", 
			    content: "View an interactive author network, an interactive objects skymap that allows you to select astronomical objects mentioned in your search results, or a word cloud formed from search results.",
			    placement:'top',
			    onShown: function(tour) {setTimeout(function(){$("a.btn.dropdown-toggle:contains(View)").trigger("click")},1000)},
			    onNext:function(tour) {$("a.btn.dropdown-toggle:contains(View)").trigger("click")}
				},
				{
				element: "a.btn.dropdown-toggle:contains(Export)", 
			    title: "Export Your Results", 
			    content: "Use this button to export your search results to the ADS Classic interface; BibTeX, AASTeX or Endnote formats; or to a personal or shared library.",
			    placement:'top',
			    onShown: function(tour) {setTimeout(function(){$("a.btn.dropdown-toggle:contains(Export)").trigger("click")},1000)},
			    onNext:function(tour) {$("a.btn.dropdown-toggle:contains(Export)").trigger("click")}
				},
				{
				element: "a.btn.dropdown-toggle:contains(Sort)", 
			    title: "Sort Your Results", 
			    content: "You can sort results by date, by citations and by popularity, and each of these can be sorted in ascending or descending order. When a sorting option is selected, an \"undo sort\" button is visible.",
			    placement:'top',
			    onShown: function(tour) {setTimeout(function(){$("a.btn.dropdown-toggle:contains(Sort)").trigger("click")},1000)},
			    onNext:function(tour) {$("a.btn.dropdown-toggle:contains(Sort)").trigger("click")}
				},
			  {
			    element: "#feedback_widget", 
			    title: "Thank You!", 
			    content: "Thank you for taking the tour of the ADS search results page. If you have any questions or comments, click here to let us know!",
			    placement:'right'
			  }
		]);
		   			
	},
	"^/abs/\\d{4}.{15}/$": function(adsTour) {
		adsTour.tour.addSteps([
				{
			    element: "li#tour", 
			    title: "Welcome to the ADS Abstract View Page", 
			    content: "Depending on the article you are currently viewing, you may not see all the possible options on this page during this tour.",
			    placement:'right'
			  },
			  {
			    element: "div.span12.abstractTitle", 
			    title: "Abstract Basics", 
			    content: "The main body of this page shows the abstract title, content, author names, and other basic bibliographic information.",
			    placement:'right'
			  },
			  	{
			    element: ".bibcodeHeader", 
			    title: "Bibcode", 
			    content: "The ADS uses bibliographic codes (bibcodes) to identify literature in our database. "
			    	+ "<a href=\"" + GlobalVariables.ADS_PREFIX + "/page/help/Filter\">Learn how an ADS bibcode is constructed.</a>",
			    placement:'right'
			  },
			  {
				element: "a.btn.dropdown-toggle:contains(Analyze)", 
			    title: "Analyze Your Results", 
			    content: "This button provides a metrics view, which shows a comprehensive set of metrics for this search result.",
			    placement:'left'
				},
				{
				element: "a.btn.dropdown-toggle:contains(Export)", 
			    title: "Export Your Results", 
			    content: "Click here to export this result in ADS Classic, BibTeX, AASTeX or Endnote.",
			    placement:'left'
				},
				{
				element: "a:contains(References)", 
			    title: "References", 
			    content: "Click this tab to view all references to other works within this article.",
			    placement:'bottom'
				},
				{
				element: "a:contains(Citations)", 
			    title: "Citations", 
			    content: "Click this tab to view all citations of this article by other works.",
			    placement:'bottom'
				},
				{
				element: "a:contains(Co-Reads)", 
			    title: "Co-Reads", 
			    content: "Click this tab to view papers that have also been read by people who read this article.",
			    placement:'bottom'
				},
				{
				element: "a:contains(Similar Articles)", 
			    title: "Similar Articles", 
			    content: "Click this tab to view other papers in ADS that have topics that are similar to the topics discussed in this article.",
			    placement:'bottom'
				},
				{
				element: "a:contains(Table of contents)", 
			    title: "Table of Contents", 
			    content: "If this article is part of a collection (a conference, book or report), this tab will show the table of contents for that collection.",
			    placement:'bottom'
				},
				{
				element: "dt:contains(Full Text Sources)", 
			    title: "Full Text Sources", 
			    content: "Find links to the full text here. Open Access resources are indicated by an open lock.",
			    placement:'left'
				},
				{
				element: "dt.recommendation", 
			    title: "Suggested Articles", 
			    content: "This list will suggest other articles with similarities in citations, usage, and topics to the current search result.",
			    placement:'left'
				},
				{
				element: "div#social_buttons", 
			    title: "Share or Store This Article", 
			    content: "This group of buttons provides direct links to ADS private libraries, Twitter, Facebook, LinkedIn and Mendeley.",
			    placement:'left'
				},
				{
			    element: "#feedback_widget", 
			    title: "Thank You", 
			    content: "Thanks for taking our tour of the ADS abstract view! If you have any questions or comments, please leave them here.",
			    placement:'right'
			 
			  }]);		
	},
	"^/search/classic-search/$": function(adsTour) {
		var authorContent = $("div#author textarea").val()
		var authorLogic= $("input:radio[name='author_logic']:checked");

		adsTour.tour.addSteps([
		  {
		    element: "li#tour", 
		    title: "Welcome to the ADS Classic Search Page", 
		    content: "This \"New Classic Search\" form offers an updated interface similar to the ADS Classic form that astronomers have been using for decades.",
		    placement:'right'
		  },
		  	{
		    element: "#classic_q", 
		    title: "A New Way to Search", 
		    content: "As you fill in the fields below, this search bar will automatically show your query as you would write it in in the ADS One-Box Search. You cannot edit this field.",
		    placement:'left'
			},
			{
		    element: "span#classic_help_button", 
		    title: "Help Mode", 
		    content: "For a more detailed description of each of the search fields, you can turn on help mode and mouse over any part of the form that interests you.",
		    onShown: function(tour) {$("span#classic_help_button").trigger("click")},
		    onNext:function(tour) {$("span#classic_help_button").trigger("click")}
		  },

		  {
		    element: "div#author textarea", 
		    title: "Try it out", 
		    content: "Type \"Berger, E\", hit return, then type \"Fong, W \" into this text field and watch as the query bar above updates automatically.",
		    placement:'right'
		  },

		  {
		    element: "div#author label.radio:eq(2)", 
		    title: "Try it Out", 
		    content: "Now that you have entered multiple authors in the form, you can choose to use 'and', 'or', or simple logic to join the names.",
		    placement:'right',
		    onShown: function(tour) {
	    							setTimeout(function(){$("div#author input.or").trigger("click")},3000);
	    							setTimeout(function(){$("div#author input.simple").trigger("click")},5000);
									setTimeout(function(){authorLogic.trigger("click")},5000)
		    						},
		    onNext:function(tour) {
		    						$("div#author textarea").val(authorContent);
		    						$("div#author textarea").trigger("click");
		    					}
		  },

		  {
		    element: "textarea#pubtext", 
		    title: "Try it Out", 
		    content: "Entering in the first few letters of either the full name or bibstem of a publication will trigger an autocomplete. Try typing the word \"astrophysical\"",
		    placement:'right',
		    onNext:function(tour) {
		    						$("textarea#pubtext").val("");
		    						$("textarea#pubtext").trigger("click");
		    					}
		  },
		  	{
		    element: "#classic_filter_div", 
		    title: "View Filters As They Are Applied", 
		    content: "Any filter you apply to your query, say, by changing the queried databases, will be reflected here immediately.",
		    placement:'left'
		  },

		  {
		    element: "#search_submit", 
		    title: "Keep in Mind this Change", 
		    content: "Unlike in the original ADS search form, individual fields within your search will be joined with an implicit \"and\" rather than an \"or\". This means everything you enter will factor in to your search results.",
		    placement:'top'
		  },

		  {
		    element: "#feedback_widget", 
		    title: "Thank You", 
		    content: "Thanks for taking the tour! If you have any questions or comments, please leave them here.",
		    placement:'right'
		  }

		  ]);
		
	}
};

