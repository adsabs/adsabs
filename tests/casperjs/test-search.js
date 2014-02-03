
/*
 * tests various functionality fo the search ui
 */

var x = require('casper').selectXPath;

casper.test.begin("testing basic search interaction", {
	test: function(test) {
		casper.start(casper.baseTestUrl, function() {
			test.assertTitle("ADS 2.0 - index");
			this.fill("#one_box_search", { q: "black holes" }, true);
		});
		casper.then(function() {
			test.assertTitle("ADS 2.0 - Search Results: black holes");
		});
		casper.run(function() {
			test.done();
		})
	}
});

casper.test.begin("testing extra search options", { 
	test: function(test) {
		casper.start(casper.baseTestUrl, function() {
			test.assertNotVisible("#advanced_options", 'advanced options hidden by default');
			this.click("#drawer_handler");
		});

		casper.then(function() {
			test.assertVisible("#advanced_options", 'click shows advanced options');
			this.fill("#one_box_search", { q: "black holes" }, true);
		});
		
		casper.then(function() {
			test.assertExists(x('//span[@class="appliedFilter"][contains(.,"astronomy OR physics")]'), 'default database filter applied')
		});
		
		casper.then(function() {
			this.fill("#one_box_search", { q: "weak lensing", db_f: "astronomy" }, true);
		})

		casper.then(function() {
			console.log(this.fetchText('.appliedFilter'));
			test.assertExists(x('//span[@class="appliedFilter"][text()="  Database :  astronomy "]'), 'selected database filter applied')
		});
		
		casper.then(function() {
			this.fill("#one_box_search", { q: "weak lensing", db_f: "" }, true);
		});

		casper.then(function() {
			console.log(this.fetchText('.appliedFilter'));
			test.assertNotExists("span.appliedFilter");
		});
		
	    casper.run(function() {
	        test.done();
	    });

	}
});