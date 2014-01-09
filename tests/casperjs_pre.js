casper.on('remote.message', function(msg) {
    this.echo('remote message caught: ' + msg);
});
casper.test.done();