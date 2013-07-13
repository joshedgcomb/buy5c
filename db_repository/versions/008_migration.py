from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
category = Table('category', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=100)),
)

image = Table('image', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('image_file', LargeBinary),
    Column('listing_id', Integer),
)

listing = Table('listing', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=140)),
    Column('body', String),
    Column('time_posted', DateTime),
    Column('user_id', Integer),
    Column('category_id', Integer),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('password', String(length=64)),
    Column('email', String(length=120)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['category'].create()
    post_meta.tables['image'].create()
    post_meta.tables['listing'].create()
    post_meta.tables['user'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['category'].drop()
    post_meta.tables['image'].drop()
    post_meta.tables['listing'].drop()
    post_meta.tables['user'].drop()
