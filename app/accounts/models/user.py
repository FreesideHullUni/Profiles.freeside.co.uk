from flask_login import UserMixin


class UserSession(UserMixin):
    def __init__(self, uid, data):
        self.id = uid
        self.data = data

    def __repr__(self):
        return self.id
