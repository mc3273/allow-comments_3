import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

NOTEBOOK_NAME = 'default_notebook'

error =""

JINJA_ENVIRONMENT = jinja2.Environment( loader = jinja2.FileSystemLoader(os.path.dirname(__file__)+ '/templates'),
                                        extensions=['jinja2.ext.autoescape'],
                                        autoescape=True)

def notebook_key(notebook_name = NOTEBOOK_NAME):
    return ndb.Key('Notebook', notebook_name)


class Message(ndb.Model):
    
    title = ndb.StringProperty(indexed = False)
    content = ndb.StringProperty(indexed = False)
    date = ndb.DateTimeProperty(auto_now_add = True)
  
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Unit1(Handler):
    def get(self):
        self.render("Unit_1.html")


class Unit2(Handler):
    def get(self):
        self.render("Unit_2.html")


class Unit3(Handler):
    def get(self):
        self.render("Unit_3.html")


class Unit4(Handler):
    def get(self):
        self.render("Unit_4.html")

        
class notesPage(webapp2.RequestHandler):
    def get(self):

        notebook_name = self.request.get('notebook_name',
                                          NOTEBOOK_NAME)
        notes_query = Message.query(
            ancestor = notebook_key(notebook_name)).order(-Message.date)
        notes = notes_query.fetch(5)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user' : user ,
            'notes' : notes ,
            'url' : url ,
            'url_linktext' : url_linktext ,
            'error' : error             
        }

        template = JINJA_ENVIRONMENT.get_template('comments.html')
        self.response.write(template.render(template_values))


class Validation(webapp2.RequestHandler):
    def post(self):
        notebook_name = self.request.get('notebook_name',
                                         NOTEBOOK_NAME)
        note = Message(parent = notebook_key(notebook_name))

        
        if not (self.request.get('content') and self.request.get('title')):
            global error
            error = "Opps you forgot to enter a  Name and some Content!"
        else:
            global error
            error = ""
            note.content = self.request.get('content')
            note.title = self.request.get('title')
            note.put()

        query_params = {'notebook_name': notebook_name}
        self.redirect('/comments.html?' + urllib.urlencode(query_params))
        


       
application = webapp2.WSGIApplication([
    ('/',Unit1),
    ('/Unit_1.html', Unit1),
    ('/Unit_2.html',Unit2),
    ('/Unit_3.html',Unit3),
    ('/Unit_4.html', Unit4),
    ('/comments.html', notesPage),
    ('/notes', Validation)
    
], debug=True)
