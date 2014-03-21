$(document).ready(function() {

    var currentPath = new Uri(window.location.href).path();
    adsTour.init(currentPath);

});

var adsTour = function() {
    return {


        flash: function(sel) {
            $(sel).animate({
                color: 'rgb(255,0,0)'
            }, 200);
            $(sel).animate({
                color: "black"
            }, 1000);
        },

        appendToQ: function(s) {
            $("input#q").val(s);
            this.flash("input#q")
        },

        removeFromQ: function() {
            $("input#q").val('');
        },

        makeTour: function(currentPath) {
            this.tour = new Tour({
                backdrop: false,
                storage: false
            });

            var tourPath = _.find(_.keys(tourSteps), function(pathKey) {
                return currentPath.replace(GlobalVariables.ADS_PREFIX, "").match(new RegExp(pathKey, "i"));
            });

            if (tourPath == undefined) return;
            var addStepsFunc = tourSteps[tourPath];
            addStepsFunc(this);
            this.tour.init();
            this.tour.start();
        },

        init: function(currentPath) {
            $("#tour").show().on("click", function(e) {
                adsTour.makeTour(currentPath);
                //pinging google analytics
                ga('send', 'event', 'tour', 'tour_initiated', currentPath)

                e.preventDefault();
            })
        }

    };
}();

var tourSteps = {
    "^\/$": function(adsTour) {
        //store the search variable if there is one
        var currentSearch = $("#q").val();

        adsTour.tour.addSteps([{
                element: "li#tour",
                title: "Welcome to the ADS Main Search Page",
                content: "This tour will show you how to write a targeted ADS query.",
                placement: 'right'
            }, {
                element: "i.icon-user",
                title: "Sign In for More Options",
                content: "You can always log in with your ADS credentials to personalize your search experience.",
                placement: 'left'
            },

            {
                element: "a:contains('Search the ADS')",
                title: "Compose Your Query",
                content: "Our new one-box query form uses both fielded and unfielded search."
            }, {
                element: "#classic-search-tab",
                title: "Classic Search",
                content: "You can click over to this tab if you'd like an interface similar to the Classic ADS form."
            }, {
                element: "#q",
                title: "Unfielded Search",
                content: "This is an example of an unfielded search. It is simple to type and will work, but the search results might be too broad.",
                onShown: function(tour) {
                    adsTour.appendToQ("redshift fizeau 1848")
                },
                placement: 'right'
            },

            {
                element: "#q",
                title: "Fielded Search",
                content: "This fielded search will yield a more precise set of results.",
                onShown: function(tour) {
                    adsTour.appendToQ("title:redshift author:fizeau year:1848")
                },
                placement: 'right'
            },

            {
                placement: 'top',
                element: "a.link_only_js:eq(0)",
                title: "Author Search",
                content: "Type author names in the form <br/>\"last, first middle initial\".",
                onShown: function(tour) {
                    adsTour.appendToQ("author:(\"huchra, j\" \"macri, l\" \"masters, k\")")
                }
            }, {
                placement: 'top',
                element: "a.link_only_js:eq(0)",
                title: "Author Search",
                content: "Because there are multiple words per name, names should be treated as phrases and each one should be surrounded with quotations."

            },

            {
                element: "a.link_only_js:eq(1)",
                title: "First Author Search",
                content: "Use a caret to search for first authors.",
                placement: 'top',
                onShown: function(tour) {
                    adsTour.appendToQ("author:\"^huchra, j\"")
                }
            }, {
                element: "a.link_only_js:eq(2)",
                title: "Title Search",
                content: "Use the title field if you have a word or phrase that should appear in the title.",
                placement: 'top',
                onShown: function(tour) {
                    adsTour.appendToQ("title:QSO")
                }
            }, {
                element: "a.link_only_js:eq(3)",
                title: "Year Search",
                content: "Date Format: YYYY or YYYY-YYYY",
                placement: 'top',
                onShown: function(tour) {
                    adsTour.appendToQ("year:1995-2000")
                }
            },

            {
                element: "a.link_only_js:eq(4)",
                title: "Publication Search",
                placement: 'top',
                content: "If you want to search for journals or other publications, you need to use abbreviations from our <a target=\"_blank\" href=\"http://adsabs.harvard.edu/abs_doc/journal_abbr.html\">bibstem list.</a>",
                onShown: function(tour) {
                    adsTour.appendToQ("bibstem:(ApJ or MNRAS)")
                }
            }, {
                element: "a.link_only_js:eq(5)",
                title: "Full Text Search",
                content: "This field performs an expansive search into the actual text of articles as well as various fields such as date, publication, and author.",
                placement: 'top',
                onShown: function(tour) {
                    adsTour.appendToQ("full:\"alien life forms\"")
                }
            }, {
                element: "a.link_only_js:eq(2)",
                title: "More Complex Queries with Parentheses",
                content: "You can use parentheses with \"and\" and \"or\" for boolean queries.",
                placement: 'top',
                onShown: function(tour) {
                    adsTour.appendToQ("title:((exoplanets or \"extrasolar planets\") and kepler)")
                }
            }, {
                element: "#tour-anchor-advanced-operators",
                title: "Advanced Search Operators",
                content: "These three operators wrap a query and give you new insight into your search. The query currently in the search bar will return a list of papers currently popular in ADS.",
                placement: 'bottom',
                onShown: function(tour) {
                    adsTour.appendToQ("trending(exoplanets)")
                }
            },

            {
                element: "#tour-anchor-advanced-operators",
                title: "Advanced Search Operators",
                content: "For a closer look at all three operators, mouse over one of the three links to read a short explanation.",
                placement: 'bottom',
                onShown: function(tour) {
                    adsTour.appendToQ(currentSearch)
                },
            },

            {
                element: "span#drawer_handler",
                title: "Advanced Options",
                content: "Click here to find filters that will help you obtain a more focused set of search results.",
                placement: 'top',
                onShown: function(tour) {
                    $("#drawer_handler").trigger("click")
                },
                onNext: function(tour) {
                    $("#drawer_handler").trigger("click")
                }
            },

            {
                element: "#feedback_widget",
                title: "Thank You for Touring the ADS Main Page",
                content: "If you have any questions or comments, click here to let us know.",
                placement: 'right'
            }
        ]);
    },
    "^/search/$": function(adsTour) {
        adsTour.tour.addSteps([{
                element: "li#tour",
                title: "Welcome to the ADS Search Results Page",
                content: "For best results with the tour, make sure you are showing multiple results from a fairly broad search term (e.g, \"exoplanets\"), and that you have not yet clicked anything on the page.",
                placement: 'right'
            }, {
                element: "div.accordion-toggle.facetAccordionHeader",
                title: "Filter Your Search Results",
                content: "This column gives you many ways to narrow your results.",
                placement: 'right'
            }, {
                element: "div.accordion-toggle:eq(2)",
                title: "authors",
                content: "If you search for an author named \"Zhang, Z\", for instance, your search might turn up results from many different individuals. A quick way to target a specific author or to exclude other authors with similar names is to click on the <i class=\"icon-chevron-right\"></i> symbol to open up a list of names that have been grouped under this name.",
                onShown: function(tour) {
                    setTimeout(function() {
                        $(".expCollSubFacetaut_f:eq(0)").trigger("click")
                    }, 2000)
                },
                placement: 'right'
            }, {
                element: "div.accordion-inner:eq(1)",
                title: "Limit Results to Specific Authors",
                content: "To limit your search to a certain author name, click on the name. To exclude an author name from your results, check the box next to the name, go to the \"apply\" button, and hit \"exclude\".",
                onNext: function(tour) {
                    $(".expCollSubFacetaut_f:eq(0)").trigger("click")
                },
                placement: 'right'
            }, {
                element: "div.accordion-toggle:eq(6)",
                title: "Limit Results to Refereed Publications",
                content: "If you wished to view only the refereed articles in your results, you could open the Refereed status filter and click on the \"refereed\" link to narrow your results.",
                placement: 'right'
            }, {
                element: "div.accordion-toggle:eq(11)",
                title: "Limit Date Range",
                content: "Or you could filter your results based on a specified year range by changing the positions of the slider toggles or entering in a year range.",
                placement: 'right'
            }, {
                element: "div.row-fluid.searchresult:eq(0) a:eq(0)",
                title: "Go to Individual Article View",
                content: "Clicking on the bibcode or title of an individual article will bring you to a page showing the abstract view for that article.",
                placement: 'top'
            }, {
                element: "div.row-fluid.searchresult:eq(0) input[type=checkbox]",
                title: "Select an Article for Aggregate Analysis",
                content: "This page provides many options for analyzing the content or metadata of a group of search results. To select one or more articles for analysis, click the checkbox next to the article.",
                placement: 'left',
                onShown: function(tour) {
                    $("div.row-fluid.searchresult:eq(0) input[type=checkbox]").trigger("click")
                },
                onNext: function(tour) {
                    $("div.row-fluid.searchresult:eq(0) input[type=checkbox]").trigger("click")
                }
            },

            {
                element: "div.row-fluid.well.well-small span.btn:eq(0)",
                title: "Select all Articles on this Page for Aggregate Analysis",
                content: "To select all articles on the current page for analysis, click this button.",
                placement: 'top',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("i.icon.icon-check").parent().trigger("click")
                    }, 1500)
                },
                onNext: function(tour) {
                    $("i.icon.icon-check").parent().trigger("click")
                }
            }, {
                element: "div.row-fluid.well.well-small div.span7.pull-right",
                title: "Default Settings for Aggregate Analysis",
                content: "If you do not select any articles for analysis, you will be offered the choice to limit your analyzed result set upon choosing your analysis or export method. We will look at different analysis and export options now.",
                placement: 'left'
            }, {
                element: "a.btn.dropdown-toggle:contains(Analyze)",
                title: "Analyze Your Results",
                content: "This button provides a citation helper, which lists articles that have cited or have been cited in your currently selected articles. The metrics view shows a comprehensive set of metrics for currently selected articles.",
                placement: 'top',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("a.btn.dropdown-toggle:contains(Analyze)").trigger("click")
                    }, 1000)
                },
                onNext: function(tour) {
                    $("a.btn.dropdown-toggle:contains(Analyze)").trigger("click")
                }
            }, {
                element: "a.btn.dropdown-toggle:contains(View)",
                title: "Visualize Your Results",
                content: "View an interactive author network or paper network, an interactive objects skymap that allows you to select astronomical objects, or a word cloud formed from your search results.",
                placement: 'top',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("a.btn.dropdown-toggle:contains(View)").trigger("click")
                    }, 1000)
                },
                onNext: function(tour) {
                    $("a.btn.dropdown-toggle:contains(View)").trigger("click")
                }
            }, {
                element: "a.btn.dropdown-toggle:contains(Export)",
                title: "Export Your Results",
                content: "Use this button to export your search results to the ADS Classic interface; BibTeX, AASTeX or Endnote formats; or to a personal or shared library.",
                placement: 'top',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("a.btn.dropdown-toggle:contains(Export)").trigger("click")
                    }, 1000)
                },
                onNext: function(tour) {
                    $("a.btn.dropdown-toggle:contains(Export)").trigger("click")
                }
            }, {
                element: "a.btn.dropdown-toggle:contains(Sort)",
                title: "Sort Your Results",
                content: "You can sort results by date, by citations and by popularity, and each of these can be sorted in ascending or descending order. When a sorting option is selected, an \"undo sort\" button is visible.",
                placement: 'top',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("a.btn.dropdown-toggle:contains(Sort)").trigger("click")
                    }, 1000)
                },
                onNext: function(tour) {
                    $("a.btn.dropdown-toggle:contains(Sort)").trigger("click")
                }
            }, {
                element: "#feedback_widget",
                title: "Thank You for Touring ADS Search Results Page",
                content: "If you have any questions or comments, click here to let us know.",
                placement: 'right'
            }
        ]);

    },
    "^/abs/\\d{4}.{15}/$": function(adsTour) {
        adsTour.tour.addSteps([{
            element: "li#tour",
            title: "Welcome to the ADS Abstract View Page",
            content: "Depending on the article you are currently viewing, you may not see all the possible options on this page during this tour.",
            placement: 'right'
        }, {
            element: "div.span12.abstractTitle",
            title: "Abstract Basics",
            content: "The main body of this page shows the abstract title, content, author names, and other basic bibliographic information.",
            placement: 'right'
        }, {
            element: ".bibcodeHeader",
            title: "Bibcode",
            content: "The ADS uses bibliographic codes (bibcodes) to identify literature in our database. " + "<a href=\"" + GlobalVariables.ADS_PREFIX + "/page/help/Filter\">Learn how an ADS bibcode is constructed.</a>",
            placement: 'right'
        }, {
            element: "a.btn.dropdown-toggle:contains(Analyze)",
            title: "Analyze Your Results",
            content: "This button provides a metrics view, which shows a comprehensive set of metrics for this search result.",
            placement: 'left'
        }, {
            element: "a.btn.dropdown-toggle:contains(Export)",
            title: "Export Your Results",
            content: "Click here to export this result in ADS Classic, BibTeX, AASTeX or Endnote.",
            placement: 'left'
        }, {
            element: "a:contains(References)",
            title: "References",
            content: "Click this tab to view all references to other works within this article.",
            placement: 'bottom'
        }, {
            element: "a:contains(Citations)",
            title: "Citations",
            content: "Click this tab to view all citations of this article by other works.",
            placement: 'bottom'
        }, {
            element: "a:contains(Co-Reads)",
            title: "Co-Reads",
            content: "Click this tab to view papers that have also been read by people who read this article.",
            placement: 'bottom'
        }, {
            element: "a:contains(Similar Articles)",
            title: "Similar Articles",
            content: "Click this tab to view other papers in ADS that have topics that are similar to the topics discussed in this article.",
            placement: 'bottom'
        }, {
            element: "a:contains(Table of contents)",
            title: "Table of Contents",
            content: "If this article is part of a collection (a conference, book or report), this tab will show the table of contents for that collection.",
            placement: 'bottom'
        }, {
            element: "#abstractRightMenu dl",
            title: "Full Text & Data Products",
            content: "If an article has associated links to fulltext or data products they will appear here. Open Access resources are indicated by an open lock.",
            placement: 'left'
        }, {
            element: "div#recommendations",
            title: "Suggested Articles",
            content: "This list will suggest other articles with similarities in citations, usage, and topics to the current search result.",
            placement: 'left'
        }, {
            element: "div#social_buttons",
            title: "Share or Store This Article",
            content: "This group of buttons provides direct links to ADS private libraries, Twitter, Facebook, LinkedIn and Mendeley.",
            placement: 'left'
        }, {
            element: "#feedback_widget",
            title: "Thank You for Touring the ADS Abstract View",
            content: "If you have any questions or comments, please leave them here.",
            placement: 'right'

        }]);
    },
    "^/search/classic-search/$": function(adsTour) {
        var authorContent = $("textarea[name=query-author-args]").val()
        var authorLogic = $("div.author-radio input:checked");
        var pubFieldContent = $("textarea[name=query-bibstem-args]").val()

        adsTour.tour.addSteps([{
                element: "li#tour",
                title: "Welcome to the ADS Classic Search Page",
                content: "This form offers an updated interface similar to the well-known ADS Classic form.",
                placement: 'right'
            }, {
                element: "#classic_q",
                title: "A New Way to Search",
                content: "As you fill in the fields below, this search bar will automatically show your query as you would write it in in the regular ADS search (accessible in the \"Search the ADS\" tab). <br/> You cannot edit this field.",
                placement: 'right'
            },

            {
                element: "textarea[name=query-author-args]",
                title: "Find Authors",
                content: "Here we are searching for papers with Edo Berger as first author and Wen-fai Fong as co-author.",
                placement: 'right',
                onShown: function(tour) {
                    $("textarea[name=query-author-args]").val("^Berger, E \n Fong, W");
                    $("textarea[name=query-author-args]").trigger("keyup");
                }
            },

            {
                element: "div.author-radio",
                title: "Changing the Logic",
                content: "Once you have entered multiple authors in the form, you can use 'and', 'or', or simple logic to join the names.",
                placement: 'right',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("div.author-radio input[value=or]").trigger("click")
                    }, 1000);
                    setTimeout(function() {
                        $("div.author-radio input[value=simple]").trigger("click")
                    }, 3000);
                    setTimeout(function() {
                        $("div.author-radio input[value=and]").trigger("click")
                    }, 5000)
                },
                onNext: function(tour) {
                    $("textarea[name=query-author-args]").val(authorContent);
                    $("textarea[name=query-author-args]").trigger("keyup");
                    authorLogic.click();
                }
            },

            {
                element: "textarea[name=query-bibstem-args]",
                title: "Limit Your Search to Certain Publications",
                content: "Entering in the first few letters of either the full name or bibstem of a publication will trigger an autocomplete. Try typing in the word \"astrophysical\".",
                placement: 'right',
                onShown: function(tour) {

                    $("textarea[name=query-bibstem-args]").val("");
                    $("textarea[name=query-bibstem-args]").trigger("keyup");
                },
                onNext: function(tour) {
                    $("textarea[name=query-bibstem-args]").val(pubFieldContent);
                    $("textarea[name=query-bibstem-args]").trigger("keyup");
                }
            }, {
                element: "#classic_filter_div",
                title: "View Filters As They Are Applied",
                content: "Any filter you apply to your query, for example, changing the queried databases, will be reflected here immediately.",
                placement: 'left',
                onShown: function(tour) {
                    setTimeout(function() {
                        $("input[name=filter-database][value=physics]").trigger("click")
                    }, 2500)
                    $("textarea[name=query-author-args]").trigger("keyup");
                    $("div.author-radio input[value=and]").trigger("click");
                },
                onNext: function(tour) {
                    $("input[name=filter-database][value=physics]").trigger("click")
                }
            },

            {
                element: "#search_submit",
                title: "Keep in Mind this Change",
                content: "Unlike in the original ADS search form, individual fields within your search will be joined with an implicit \"and\" rather than an \"or\". This means everything you enter will factor in to your search results.",
                placement: 'bottom'
            },

            {
                element: "#feedback_widget",
                title: "Thank You for Touring the New Classic Search Form",
                content: "If you have any questions or comments, please leave them here.",
                placement: 'right'
            }

        ]);

    }
};