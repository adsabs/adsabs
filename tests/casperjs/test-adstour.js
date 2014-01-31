
/*
 * This test checks that all jquery/css selectors used by the adstour
 * are present in the pages they are associated with
 */

function checkSteps() {
	var currentPath = new Uri(window.location.href).path();
	console.log("checking tour steps for " + currentPath);
	adsTour.makeTour(currentPath);
	
	// fail if no tour was loaded
	if (!adsTour.tour._steps.length) return false;

	var found = 0
	_.each(adsTour.tour._steps, function(step) {
		var sel = step['element'];
		console.log("checking '" + sel + "'");
		if ($(sel).length) {
			found++;
		} else {
			console.log("missing: '" + sel + "'");
		}
	});
	console.log("needed: " + adsTour.tour._steps.length + ", got: " + found);
	return found == adsTour.tour._steps.length;
}

casper.test.begin("testing adstour.js steps", {
	test: function(test) {
		casper.start(casper.baseTestUrl + "/", function() {
			test.assertEval(checkSteps);
			this.fill('#one_box_search', { q: 'black holes' }, true);
		});
		casper.then(function() {
			test.assertEval(checkSteps);
		});
		casper.thenOpen(casper.baseTestUrl + "/search/classic-search/", function() {
			test.assertEval(checkSteps);
		});
		casper.thenOpen(casper.baseTestUrl + "/abs/2314ADS..4305...27Q/", function() {
			test.assertEval(checkSteps);
		});
	    casper.run(function() {
	        test.done();
	    });

	}
})
