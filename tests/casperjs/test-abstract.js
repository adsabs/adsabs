
var x = require('casper').selectXPath;

casper.test.begin("testing abstract view", {
	test: function(test) {
		casper.start(casper.baseTestUrl, function() {
			this.fill("#one_box_search", { q: "useful(weak lensing)", db_f: "astronomy" }, true);
		});
		
		// grab the bibcode of the first result to compare on subsequent page
		var bibcode;

		casper.then(function() {
			// click the first abstract link
			bibcode = casper.evaluate(function() {
				return $(".searchresult .bibcode a:first").text();
			});
			this.click(".searchresult .bibcode a");
		});

		casper.then(function() {
			test.assertExists(x('//div[contains(@class,"bibcodeHeader")][text()="' + bibcode + '"]'));
		});
		casper.run(function() {
			test.done();
		})
	}
});