casper.on('remote.message', function(msg) {
    this.echo('remote message caught: ' + msg);
});

casper.baseTestUrl = casper.cli.has("baseTestUrl")
    ? casper.cli.get("baseTestUrl")
    : "http://localhost:5000";

