var x = require('casper').selectXPath;

casper.test.begin("testing abstract view", {
	test: function(test) {
		casper.start(casper.baseTestUrl, function() {
			this.fill("#one_box_search", { q: '"GO9-0102X"' }, true);
		});
		casper.then(function() {
			test.assertExists(x("//span[contains(@class,'highlight')][contains(.,'GO9-0102X')]"));
		});
		casper.then(function() {
			this.fill("#one_box_search", { q: 'full:"GO9-0102X"' }, true);
		});
		casper.then(function() {
			test.assertExists(x("//span[contains(@class,'highlight')][contains(.,'GO9-0102X')]"));
		});
		casper.then(function() {
			this.fill("#one_box_search", { q: 'shapley bibcode:1913AN....196..385S' }, true);
		});
		casper.then(function() {
			this.capture('result.png')
			test.assertExists(x("//span[contains(@class,'highlight')][contains(.,'Shapley')]"));
		});
		casper.run(function() {
			test.done();
		})		
	}
});