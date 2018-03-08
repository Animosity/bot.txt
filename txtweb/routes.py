from txtweb import txtweb

@txtweb.route('/')
def index():
    return "Hello dad"