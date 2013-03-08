import logging
#import fix_path

import os
from google.appengine.ext.webapp import template

import cgi
import datetime
import urllib
import wsgiref.handlers

#from google.appengine.ext import db
#from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#class Greeting(db.Model):
#  """Models an individual Guestbook entry with an author, content, and date."""
#  author = db.StringProperty()
#  content = db.StringProperty(multiline=True)
#  date = db.DateTimeProperty(auto_now_add=True)
#

#def guestbook_key(guestbook_name=None):
#  """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
#  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp.RequestHandler):
    def get(self):
##        guestbook_name=self.request.get('guestbook_name')
##        greetings_query = Greeting.all().ancestor(
##            guestbook_key(guestbook_name)).order('-date')
##        greetings = greetings_query.fetch(10)
#
#        if users.get_current_user():
#            url = users.create_logout_url(self.request.uri)
#            url_linktext = 'Logout'
#        else:
#            url = users.create_login_url(self.request.uri)
#            url_linktext = 'Login'
#
        template_values = {
#            'greetings': greetings,
#            'url': url,
#            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


#class Guestbook(webapp.RequestHandler):
#  def post(self):
#    # We set the same parent key on the 'Greeting' to ensure each greeting is in
#    # the same entity group. Queries across the single entity group will be
#    # consistent. However, the write rate to a single entity group should
#    # be limited to ~1/second.
#    guestbook_name = self.request.get('guestbook_name')
#    greeting = Greeting(parent=guestbook_key(guestbook_name))
#
#    if users.get_current_user():
#      greeting.author = users.get_current_user().nickname()
#
#    greeting.content = self.request.get('content')
#    greeting.put()
#    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

class UploadHandler(webapp.RequestHandler):
    def post(self):
      #csvFile = open(self.request.get('csvUpload',default_value=''), 'rb').read()
      
      from StringIO import StringIO
      import csv
      import icsConverter

      csvFile = csv.reader(StringIO(self.request.get('csvUpload', default_value='')))      
      icsFile = icsConverter.convert(csvFile)
#     Looks to be working like a charm      
#      logging.info("Here is icsFile: %s", icsFile)
      icsFileJS = icsFile.replace('\r\n','\\n\\\r')

      if icsFile:
#        DownloadHandler().get(icsFile)
#        print icsFile

         self.response.out.write('''
        <html>
          <body>
            <p>Working!</p>
            <textarea rows="4" cols="50">Lorem Ipsum</textarea>
            <script type = "text/javascript">
        var Download = {
    click : function(node) {
        var ev = document.createEvent("MouseEvents");
        ev.initMouseEvent("click", true, false, self, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
        return node.dispatchEvent(ev);
    },
    encode : function(data) {
            return 'data:application/octet-stream;base64,' + btoa( data );
    },
    link : function(data, name){
        var a = document.createElement('a');
        a.download = name || self.location.pathname.slice(self.location.pathname.lastIndexOf('/')+1);
        a.href = data || self.location.href;
        return a;
    }
};
Download.save = function(data, name){
    this.click(
        this.link(
            this.encode( data ),
            name
        )
    );
};


icsData = '%s';

Download.save(icsData, 'Output.ics');
</script> 
          </body>
        </html>
        ''' % icsFileJS)
        
#        self.redirect("/success/?icsFile=" + icsFile)
      else:
        self.redirect("/failure")

#class DownloadHandler(webapp.RequestHandler):
#    def get(self):
##        pass
#
#        
##        message = "Hello, some stuff here."
##        print message
#        icsFile = urllib.unquote(self.request.get('icsFile'))
#        
#        template_values = {
#          'icsFile': icsFile,
#        }
#
#        path = os.path.join(os.path.dirname(__file__), 'success.html')
#        self.response.out.write(template.render(path, template_values))
#        
#        print "Attempt 3: " + icsFile
        
#        if icsFile:
#          self.redirect("/success.html")
#          self.response.headers['Content-Type'] = 'text/calendar'
#          self.response.headers['Content-Disposition'] = 'attachment; filename=OutputFile.ics'
#          self.response.out.write(icsFile)        

application = webapp.WSGIApplication([
#  ('/success', DownloadHandler),
  ('/upload', UploadHandler),
  ('/', MainPage)
#  ('/sign', Guestbook)
], debug=True)


def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()