import os
import kai.res
from flask import request, Response


# setup the static web server response handlers
def setup_static_web(app):

    @app.route('/', methods=['GET'])
    @app.route('/index.html', methods=['GET'])
    @app.route('/login.html', methods=['GET'])
    @app.route('/query.html', methods=['GET'])
    @app.route('/entities.html', methods=['GET'])
    @app.route('/favicon.ico', methods=['GET'])
    def index():  # pragma: no cover
        page = request.url.split('/')[-1]
        mime_type = 'text/html'
        if len(page) == 0:
            page = 'index.html'
        if page.endswith(".ico"):
            mime_type = "image/x-icon"
            content = open(kai.res.filename('web/' + page), 'rb').read()
        else:
            content = open(kai.res.filename('web/' + page)).read()
        return Response(content, mimetype=mime_type)
    
    
    @app.route('/css', defaults={'path': ''})
    @app.route('/css/<path:path>')
    def get_css(path):  # pragma: no cover
        complete_path = kai.res.filename('web/css/' + path)
        if os.path.exists(complete_path):
            content = open(complete_path).read()
            return Response(content, mimetype="text/css")
        else:
            return Response("resource not found", status=404)
    
    
    @app.route('/fonts', defaults={'path': ''})
    @app.route('/fonts/<path:path>')
    def get_fonts(path):  # pragma: no cover
        font_mime_types = {'svg': 'image/svg+xml', 'ttf': 'font/ttf',
                           'woff': 'application/x-font-woff',
                           'woff2': 'application/x-font-woff'}
        complete_path = kai.res.filename('web/fonts/' + path)
        if os.path.exists(complete_path):
            content = open(complete_path, 'rb').read()
            mime_type = font_mime_types[path.split('.')[1]]
            return Response(content, mimetype=mime_type)
        else:
            return Response("resource not found", status=404)
    
    
    @app.route('/images', defaults={'path': ''})
    @app.route('/images/<path:path>')
    def get_images(path):  # pragma: no cover
        complete_path = kai.res.filename('web/images/' + path)
        if os.path.exists(complete_path):
            content = open(complete_path, 'rb').read()
            mime_type = 'image/png'
            if path.endswith('.jpg'):
                mime_type = 'image/jpeg'
            return Response(content, mimetype=mime_type)
        else:
            return Response("resource not found", status=404)
    
    
    @app.route('/js', defaults={'path': ''})
    @app.route('/js/<path:path>')
    def get_js(path):  # pragma: no cover
        complete_path = kai.res.filename('web/js/' + path)
        if os.path.exists(complete_path):
            content = open(complete_path).read()
            return Response(content, mimetype='application/javascript')
        else:
            return Response("resource not found", status=404)
    
    
