
casper.test.begin('searching lobbyist represents', 2, function suite(test) {
    casper
        .start('http://localhost:8000/lobbyist/124')
        .then(function() {
            test.assert(casper.getElementsInfo('section.lobbyist-represents li:not(.hidden)').length > 1)
        })
        .then(function(){
            casper.sendKeys('#lobbyist-company-search input', 'WJ Technologies');
        })
        .waitFor(function(){
            return casper.getElementsInfo('section.lobbyist-represents li:not(.hidden)').length == 1;
        }, function() {
            test.assertSelectorHasText('section.lobbyist-represents li:not(.hidden)', 'WJ Technologies');
        }, function() {
            test.fail('did not get a single li element for the lobbyist represents')
        })
        .run(function(){
            test.done();
        });
});
