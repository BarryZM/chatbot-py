from sqlalchemy import Column, Integer, String, DateTime, ForeignKey  # Text, Table
# from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr, declarative_base


class ModelBase:
    """
    An augmented base class for SqlAlchemy models.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        table_name = ''
        for index, char in enumerate(cls.__name__):
            if index == 0:
                table_name += char.lower()
            else:
                if char.isupper():
                    table_name += '_{}'.format(char.lower())
                else:
                    table_name += char

        return table_name

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )


Base = declarative_base(cls=ModelBase)


class Statement(Base):
    question = Column(
        String(length=1000),
        unique=True
    )
    answer = Column(
        String(length=1000),
        nullable=False
    )
    category = Column(
        String(length=100),
        server_default='其他'
    )
    type = Column(
        Integer,
        server_default='0'
    )
    parameters = Column(
        String(length=255),
        server_default=''
    )
    extractor = Column(
        String(length=255),
        server_default=''
    )
    create_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Tag(Base):
    """
    A tag that describes a statement.
    """

    name = Column(
        String(length=255),
        unique=True
    )


class TagAssociationStatement(Base):
    tag_id = Column(
        Integer,
        ForeignKey('tag.id')
    )
    statement_id = Column(
        Integer,
        ForeignKey('statement.id')
    )


class AccessLog(Base):
    statement_id = Column(
        Integer,
        ForeignKey('statement.id')
    )
    access_time = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


statement_table_name = Statement.__tablename__
tag_table_name = Tag.__tablename__
tag_association_statement_table_name = TagAssociationStatement.__tablename__
access_log_table_name = AccessLog.__tablename__
