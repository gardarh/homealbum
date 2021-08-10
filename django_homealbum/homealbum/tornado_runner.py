# Run this with
# DJANGO_ALLOW_ASYNC_UNSAFE=true PYTHONPATH=. [copy all env variables from .env.local into this line] python homealbum/tornado_runner.py --port=1234
import tornado.httpserver
import tornado.web
import tornado.wsgi
import django.core.handlers.wsgi
from django.conf import settings
import tornado.ioloop
from tornado.options import define, parse_command_line, options

django.setup()

MULTI_CORE = True
TORNADO_PORT = 9998
define('port', type=int, default=TORNADO_PORT)


def main():
    parse_command_line()
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

    tornado_app = tornado.web.Application([
        (r"/originals/(.*)", tornado.web.StaticFileHandler, {'path': settings.PHOTOS_BASEDIR}),
        (r"/thumbs/(.*)", tornado.web.StaticFileHandler, {'path': settings.PHOTOS_THUMBS_BASEDIR}),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': settings.STATIC_ROOT}),
        (r".*", tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    ])
    print("Tornado server running on port %d, multiple processes: %s" % (options.port, MULTI_CORE))
    if MULTI_CORE:
        server = tornado.httpserver.HTTPServer(tornado_app)
        server.bind(options.port)
        server.start(0)
    else:
        tornado_app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
