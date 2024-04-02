from enum import Enum

from sqlalchemy import create_engine
import sqlalchemy as sa
from aiohttp_admin2.connection_injectors import ConnectionInjector


metadata = sa.MetaData()
postgres_injector = ConnectionInjector()


class PostStatusEnum(Enum):
    published = 'published'
    not_published = 'not published'


users = sa.Table('demo_quick_users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('first_name', sa.String(255)),
    sa.Column('last_name', sa.String(255)),
    sa.Column('is_superuser', sa.Boolean),
    sa.Column('joined_at', sa.DateTime()),
)

post = sa.Table('demo_quick_post', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('title', sa.String(255)),
    sa.Column('body', sa.Text),
    sa.Column('status', sa.Enum(PostStatusEnum)),
    sa.Column('published_at', sa.DateTime()),
    sa.Column('author_id', sa.ForeignKey('demo_quick_users.id', ondelete='CASCADE')),
)

DB_URL = 'postgresql://postgres:postgres@0.0.0.0:5432/postgres'


def create_tables(db_url):
    engine = create_engine(
        db_url,
        isolation_level='AUTOCOMMIT',
    )

    metadata.create_all(engine)


def recreate_tables(db_url):
    engine = create_engine(
        db_url,
        isolation_level='AUTOCOMMIT',
    )

    metadata.drop_all(engine)
    metadata.create_all(engine)


if __name__ == '__main__':
    recreate_tables(DB_URL)
