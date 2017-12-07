# A class to track all connected users.  Everytime a user switches to another
# page, the table of active users will be updated, because a user will
# disconnect and reconnect on a page switch.  If we to write a single-page
# application, we could avoid these reconnect/disconnects. A user might be
# logged in several times (e.g., on different machines), so we maintain a list
# of connections per user.
class ActiveUsers():

    def __init__(self):
       self.active_users = {}

    def add_user(self, name, sid):
        if not self.active_users.has_key(name):
            self.active_users[name] = []
        self.active_users[name].append(sid)

    def del_user(self, name, sid):
        if self.active_users.has_key(name):
            self.active_users[name].remove(sid)

    def is_connected(self, name):
        return name in self.active_users

    def get_sids(self, name):
        return self.active_users[name]