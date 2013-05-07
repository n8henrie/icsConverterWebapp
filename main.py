from __future__ import with_statement

from google.appengine.api import files
from google.appengine.ext.webapp import template, blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb, blobstore, ereporter

import wsgiref.handlers
import webapp2

import os
import datetime
import logging

# Setting up for better exception handling,
# but not used as of May 06, 2013.
ereporter.register_logger()

class MainPage(webapp2.RequestHandler):
    def get(self, success_status=None, blob_key=None):

        # Default set of URLs to display below form.
        urls = {
            'icsConverterWebapp Instructional Post':
            'http://n8henrie.com/2013/05/spreadsheet-to-calendar/',
            'icsConverter (OSX Desktop Version)':             'http://n8henrie.com/2013/05/spreadsheet-to-calendar#icsConverter',
            'icsConverterWebapp at GitHub':
            'https://github.com/n8henrie/icsConverterWebapp',
            'icsConverter at GitHub':
            'https://github.com/n8henrie/icsConverter',
            }

        # Default welcome message.
        if success_status == None:
            message = '<p>Welcome to my first attempt at a webapp! <br />If you need instructions, please see the blog post <a target="_blank" href="http://nhenrie.com/">here</a>.</p>'

            # Option to append extra URLs based on success_status
#            urls.update({ 'another url': 'http://fake.com' })

        if success_status == 'success':
            message = '''<p>Amazingly... it looks like it may have worked. Click [<a href='/download/{0}'>here</a>], then check your downloads folder for a file named "converted.ics". <b>Before importing to your primary calendar, I highly recommend you either inspect it in a text editor and/or import it into a junk calendar.</b></p><p>While I can\'t think of a way this could lead to data loss, I\'m sure that it\'s possible, and it could most certainly lead to a buch of junk calendar events that would be a pain to (manually) clean out. So create a new calendar and import it there, just to be safe. If it works, delete that junk calendar and import to your real one.</p><p>Hope you\'ve found icsConverterWebapp helpful!</p>'''.format(blob_key)

            # Option to append extra URLs based on success_status
#            urls.update({ 'another url': 'http://fake.com' })

        if success_status == 'failure':

            # Error messages based on blob_key if success_status
            # is failure. This is probably horrible coding practice.
            error_dict = {
            'uploadfail': 'that might not have been a .csv file, because it didn\'t even get through the uploading step.',
            'error1': 'either the file wasn\'t a proper .csv file, or the headers were not *exactly* right.',
            'error2': 'the headers looked okay, but something went wrong in the actual file conversion. Take a close look at all start and end dates to verify they are in MM/DD/YYYY format (this is easily changed by any modern spreasheeting app, including Google Docs).',
            'error3': 'there was some kind of problem finalizing the file. This is a rare error, please let me know if you\'re getting it repeatedly.',
            }

            # Framework for error message.
            message = '''<p>Well, something didn't work right.</p><p>If I had to guess, I would say {0}</p><p>I <em>highly</em> recommend you read the instructional post (below) at least once.</p>'''.format(error_dict[blob_key])

            # Option to append extra URLs based on success_status
#            urls.update({ 'another url': 'http://fake.com' })

        template_values = {
        'message': message,
        'urls': urls,
        }


        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class StoreFile(ndb.Model):
#    FileName = ndb.StringProperty()
    BlobKey = ndb.BlobKeyProperty()

class UploadHandler(webapp2.RequestHandler):
    def post(self):

        from StringIO import StringIO
        import csv
        import icsConverterWebapp

        csvFile = None
        icsFile = None

        up_file = self.request.get('csvUpload',
        default_value='')

        try:
            # Read up_file as a csv dictionary.
            csvFile = list(csv.DictReader(StringIO(up_file),
            skipinitialspace = True))

        except:
            return self.redirect('/failure/uploadfail')

        icsFile = icsConverterWebapp.convert(csvFile)

        # icsConverterWebapp.py returns icsFile as error1-3
        # if it has a problem.
        if icsFile[0:5] == 'error':
            self.redirect('/failure/%s' % icsFile)

        elif icsFile:

            # Create a blob from the converted file.
            ics_blob = files.blobstore.create(mime_type =
            'application/octet-stream')

            with files.open(ics_blob, 'a') as f:
              f.write(icsFile)

            files.finalize(ics_blob)

            # Get the blob key
            blob_key = files.blobstore.get_blob_key(ics_blob)

            f = StoreFile(BlobKey = blob_key)

            f.put()

            self.redirect('/success/%s' % blob_key)

        else:
            print 'There was no icsFile!'

class DLHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):

        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blob_key,save_as='converted.ics')

application = webapp2.WSGIApplication(routes=[
    webapp2.Route(r'/upload', handler=UploadHandler, name='Upload'),
    webapp2.Route(r'/download/<blob_key:[a-zA-Z0-9_=.+-]+>', handler=DLHandler, name='Download'),
webapp2.Route(r'/<success_status:(success|failure)>/<blob_key:[a-zA-Z0-9_=.+-]+>', handler=MainPage, name='Success-Failure'),
    webapp2.Route(r'/', handler=MainPage, name='MainPage'),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
