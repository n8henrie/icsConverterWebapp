import os
from google.appengine.ext.webapp import template
import cgi
import datetime
import urllib
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    def get(self):

            template_values = {
            }

            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))

class UploadHandler(webapp.RequestHandler):
    def post(self):

        from StringIO import StringIO
        import csv
        import icsConverterWebapp

        csvFile = list(csv.DictReader(StringIO(self.request.get('csvUpload', default_value='')), skipinitialspace = True))

        icsFile = icsConverterWebapp.convert(csvFile)

        icsFileJS = icsFile.replace('\r\n','\\n\\\r')

        if icsFile:
            self.response.headers['Content-Type'] = "application/ics"
            self.response.headers['Content-Disposition'] = 'attachment; filename=calendar.ics'
            self.response.write(icsFile)

        else:
            self.redirect("/failure")

application = webapp.WSGIApplication([
    ('/upload', UploadHandler),
    ('/', MainPage)
], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
