from collections import namedtuple


User = namedtuple('User', ['username', 'id', 'password', 'permission'])


users = [
    User('admin', 1, 'admin', ['admin']),
    User('simple', 2, 'simple', []),
]

user_map = {
    user.username: user for user in users
}
