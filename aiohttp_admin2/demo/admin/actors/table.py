import sqlalchemy as sa


metadata = sa.MetaData()

actors = sa.Table('actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)
