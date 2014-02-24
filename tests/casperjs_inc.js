casper.on('remote.message', function(msg) {
    this.echo('remote message caught: ' + msg);
});

casper.baseTestUrl = casper.cli.has("baseTestUrl")
    ? casper.cli.get("baseTestUrl")
    : "http://localhost:5000";

casper.options.stepTimeout = casper.cli.has('stepTimeout')
	? casper.cli.options.stepTimeout
	: 5000;

casper.echo('baseTestUrl: ' + casper.baseTestUrl);
casper.echo('stepTimeout: ' + casper.options.stepTimeout);