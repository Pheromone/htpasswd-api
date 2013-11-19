#-=- encoding: utf-8 -=-
from flask import Flask
from flask import request
from flask.ext import restful
from htpasswd import Basic as auth
from path import path
import logging
import slugify

app = Flask(__name__)
api = restful.Api(app)
PORT = 7000
IP = '127.0.0.1'
DEBUG = True
#PASSWORDS_PATH = '/etc/nginx/passwords'
PASSWORDS_PATH = '.'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('htpasswdapi.log')
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


class Lists(restful.Resource):
    # Get all the lists
    def get(self):
        return {'lists': path(PASSWORDS_PATH).files()}

    # Add a new list
    def post(self):
        slug = slugit(request.json['name'])
        path.touch('{}/{}'.format(PASSWORDS_PATH, slug))
        return {'list': slug}


class List(restful.Resource):
    # Gets a single list with all the user in it
    def get(self, _slug):
        with auth(PASSWORDS_PATH + _slug) as usersdb:
            return {'users': usersdb.users}

    # Adds a user to the list
    def post(self):
        _slug = request.json['slug']
        with auth(PASSWORDS_PATH + _slug) as usersdb:
            username = request.json['username']
            password = request.json['password']
            usersdb.add(username, password)
            return {'users': usersdb.users}


class Users(restful.Resource):
    # Update a user on a list
    def put(self, list_slug, username):
        with auth(PASSWORDS_PATH + list_slug) as usersdb:
            password = request.json['password']
            usersdb.change_password(username, password)
            return {}, 200

    # Deletes a user from the list
    def delete(self, list_slug, username):
        with auth(PASSWORDS_PATH + list_slug) as usersdb:
            usersdb.pop(username)
            return {}, 200

api.add_resource(Lists, '/')
api.add_resource(List, '/<string:slug>')
api.add_resource(Users, '/<string:list_slug>/<string:username>')

if __name__ == '__main__':
    app.run(host=IP, port=PORT, debug=DEBUG)
