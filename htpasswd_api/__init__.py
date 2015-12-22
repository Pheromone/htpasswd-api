# -=- encoding: utf-8 -=-
from flask import Flask
from flask import request
from flask.ext import restful
from htpasswd import Basic as auth
from path import path
from htpasswd_api.models import List
import logging
import slugify
import os

here = lambda * x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)
app = Flask(__name__)
api = restful.Api(app)
PORT = 7000
IP = '127.0.0.1'
DEBUG = os.environ.get('DEBUG', "1") == "1"
# PASSWORDS_PATH = '/etc/nginx/passwords'
PASSWORDS_PATH = os.environ.get('PASSWORDS_PATH', here() + '/passwords')
LOGS = os.environ.get('LOGS', '{}/htpasswdapi.log'.format(here()))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(LOGS)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def slugit(string):
    if type(string) == str:
        string = unicode(string)
    return slugify.slugify(string)


@app.before_request
def autoclean():
    if request.json and 'slug' in request.json:
        request.json['slug'] = slugit(request.json['slug'])


class ListsApi(restful.Resource):
    lists = []

    def __init__(self):
        self._refresh()

    def _refresh(self):
        self.lists = []
        for htpasswd in path(PASSWORDS_PATH).files():
            htlist = List(unicode(htpasswd.name), htpasswd)
            self.lists.append(htlist)

    # Get all the lists
    def get(self):
        logger.debug(self.lists)
        return {'lists': [htlist.__json__() for htlist in self.lists]}

    # Add a new list
    def post(self):
        slug = slugit(request.json['name'])
        logger.debug('Adding list {}'.format(slug))
        path('{}/{}'.format(PASSWORDS_PATH, slug)).touch()
        return {'list': slug}


class ListApi(restful.Resource):
    # Gets a single list with all the user in it
    def get(self, slug):
        htlist = path(PASSWORDS_PATH + '/' + slug)
        htpassword = List(htlist.name, htlist)
        return {'users': [{'username': user} for user
                          in htpassword.users], 'slug': slug}

    def delete(self, slug):
        htlist = path(PASSWORDS_PATH + '/' + slug)
        htlist.remove()
        return 200

    # Adds a user to the list
    def post(self, slug):
        with auth(PASSWORDS_PATH + '/' + slug) as usersdb:
            username = request.json['username']
            password = request.json['password']
            usersdb.add(username, password)
            return {'users': usersdb.users}


class UsersApi(restful.Resource):
    # Update a user on a list
    def put(self, list_slug, username):
        with auth(PASSWORDS_PATH + list_slug) as usersdb:
            password = request.json['password']
            usersdb.change_password(username, password)
            return {}, 200

    # Deletes a user from the list
    def delete(self, list_slug, username):
        with auth(PASSWORDS_PATH + '/' + list_slug) as usersdb:
            print username
            usersdb.pop(username)
            return {}, 200

api.add_resource(ListsApi, '/')
api.add_resource(ListApi, '/<string:slug>')
api.add_resource(UsersApi, '/<string:list_slug>/<string:username>')
