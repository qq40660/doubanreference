import sae
from doubanreference import wsgi

application = sae.create_wsgi_app(wsgi.application)
