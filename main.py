import os
import cgi
import urllib

from django.utils import simplejson

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Home(webapp.RequestHandler):
    def get(self):
        context = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, context))

class SearchResults(webapp.RequestHandler):
    def get(self):
        q = self.request.get('q')        
        start = self.request.get('start', None)
        query = urllib.urlencode({'q' : q})
        if start:
            query = query + ("&start=%s" % start)
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=active&%s' % (query)
        search_results = urllib.urlopen(url)
        json = simplejson.loads(search_results.read())
        results = json['responseData']['results']
        cursor = json['responseData']['cursor']
        results_ctx = []
        for i in results:
            results_ctx.append({
                'title': i['title'], 
                'url': i['url'],
                'content': i['content']
            })
        context = {
            'results': results_ctx,
            'cursor': cursor,
            'current_page': cursor['currentPageIndex'] + 1,
            'next_start': (cursor['currentPageIndex'] + 1) * 4,
            'prev_start': (cursor['currentPageIndex'] - 1) * 4,
            'q': q
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/results.html')
        self.response.out.write(template.render(path, context))

def main():
    # logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication(
         [
         ('/', Home),
         ('/search', SearchResults),     
         ],
         # debug=True
    )
    run_wsgi_app(application)

if __name__ == "__main__":
    main()