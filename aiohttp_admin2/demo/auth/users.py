from collections import namedtuple


User = namedtuple('User', ['username', 'password'])


# todo: move to database
users = [
    User('admin', 'admin')
]
