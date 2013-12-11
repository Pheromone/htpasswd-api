#-=- encoding: utf-8 -=-
from htpasswd import Basic as auth


class List():
    slug = None
    users = []
    path = None

    def __init__(self, slug, path):
        self.slug = slug
        self.path = path
        self._refresh()

    def _refresh(self):
        with auth(self.path) as userdb:
            self.users = userdb.users

    def __json__(self):
        return dict(slug=self.slug, users=self.users)
