casper.on('remote.message', function(msg) {
    this.echo('remote message caught: ' + msg);
});

casper.baseTestUrl = casper.cli.has("baseUrl")
    ? casper.cli.get("baseUrl")
    : "http://localhost:5000";

casper.test.done();