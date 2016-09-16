import jinja2
import os
import webapp2

from google.appengine.ext import db

templateDir = os.path.join(
    os.path.dirname(__file__), "templates"
)
jinjaEnv = jinja2.Environment(
    loader = jinja2.FileSystemLoader(templateDir),
    autoescape = True
)

class Post(db.Model):
    title   = db.StringProperty(required = True)
    body    = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BaseHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect("/blog")

class Index(webapp2.RequestHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC "
                            "LIMIT 5 ")

        t = jinjaEnv.get_template("index.html")
        response = t.render(posts = posts)
        self.response.write(response)

class NewPostHandler(webapp2.RequestHandler):
    def renderNewPostForm(self, title = "", body = "", error = ""):
        t = jinjaEnv.get_template("newpost.html")
        response = t.render(
            title = title,
            body  = body,
            error = error
        )
        self.response.write(response)

    def get(self):
        self.renderNewPostForm()

    def post(self):
        title = self.request.get("title")
        body  = self.request.get("body")

        if not title or not body:
            self.renderNewPostForm(
                title = title,
                body  = body,
                error = "Not all forms filled out.  Try again."
            )
        else:
            p = Post(title = title, body = body)
            p.put()
            self.redirect("/blog/{}".format(p.key().id()))

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))

        t = jinjaEnv.get_template("viewpost.html")
        response = t.render(post = post)
        self.response.write(response)

app = webapp2.WSGIApplication([
    ("/", BaseHandler),
    ("/blog", Index),
    ("/newpost", NewPostHandler),
    webapp2.Route("/blog/<id:\d+>", ViewPostHandler)
], debug = True)
