from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)

Base = declarative_base()

"""
many to one _> one to many
many to many
"""

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


# todo POST table
class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False, unique=False)
    write_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer")
    tags = relationship('Tag', secondary=tag_post)


# todo TAG table
# todo Comment table

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    posts = relationship('Post', secondary=tag_post)


# todo Writer table
class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=False)
    url = Column(String, nullable=False, unique=True)
    posts = relationship("Post")
