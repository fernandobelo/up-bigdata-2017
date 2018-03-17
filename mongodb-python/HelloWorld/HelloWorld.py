import bottle

@bottle.route('/')
def home_page():
    return "<html><title>Hello</title><body><b>Hello World</b>\n</body></html>"

@bottle.route('/testpage')
def test_page():
    return "this is a test page"

bottle.debug(True)
bottle.run(host='localhost',port=8082)