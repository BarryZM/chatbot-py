import logging
from sqlalchemy import create_engine  # and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection
# from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .models import Base, Statement, Tag, TagAssociationStatement, AccessLog
from .exceptions import DeleteDataWithoutConditionError, ModelNotExistError, ExecuteSqlError
from .constants import DEFAULT_DATABASE_URI


class SQLStorage:
    """
    The SQLStorageAdapter allows ChatterBot to store conversation
    data in any database supported by the SQL Alchemy ORM.

    All parameters are optional, by default a sqlite database is used.

    It will check if tables are present, if they are not, it will attempt
    to create the required tables.

    :keyword database_uri: eg: sqlite:///database_test.sqlite3',
        The database_uri can be specified to choose database driver.
    :type database_uri: str
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger', logging.getLogger(__name__))
        self.database_uri = kwargs.get('database_uri', None)

        # Create a file database if the database is not a connection string
        if not self.database_uri:
            self.database_uri = DEFAULT_DATABASE_URI

        # connect db
        self.engine = create_engine(self.database_uri, encoding='utf8', echo=False)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=True)
        if not self.engine.dialect.has_table(self.engine, 'statement'):
            self.create_database()

    def get_model(self, model_name):
        """
        Return the model class for a given model name.

        model_name is case insensitive.
        """
        get_model_method = getattr(self, 'get_{}_model'.format(model_name.lower()), None)

        if not get_model_method:
            raise ModelNotExistError(model_name)

        return get_model_method()

    @staticmethod
    def get_statement_model():
        """
        Return the statement model class
        """
        return Statement

    @staticmethod
    def get_tag_model():
        """
        Return the tag model class
        """
        return Tag

    @staticmethod
    def get_tag_association_statement_model():
        """
        Return the tag_association_statement model class
        """
        return TagAssociationStatement

    @staticmethod
    def get_access_log_model():
        """
        Return the tag_association_statement model class
        """
        return AccessLog

    def create_database(self):
        """
        Populate the database with the tables.
        """
        Base.metadata.create_all(self.engine)

    def count(self, model_name):
        """
        Return the number of entries in the database.
        """
        model = self.get_model(model_name)

        session = self.Session()
        model_count = session.query(model).count()
        session.close()
        return model_count

    def create(self, model_name, **kwargs):
        """
        add data to the database
        """
        model = self.get_model(model_name)
        session = self.Session()
        model_new_data = model(**kwargs)
        session.add(model_new_data)
        session.commit()
        id_ = model_new_data.id
        session.close()
        return id_
        # return list(self.filter(model_name, id=id))[0]

    def delete(self, model_name, **kwargs):
        """
        delete matching data from the database
        """
        # Report error without query conditions
        if not kwargs:
            raise DeleteDataWithoutConditionError()
        model = self.get_model(model_name)
        session = self.Session()
        session.query(model).filter_by(**kwargs).delete()
        session.commit()
        session.close()

    def filter(self, model_name, to_dict=False, **kwargs):
        model = self.get_model(model_name)
        session = self.Session()
        all_filter_object = session.query(model).filter_by(**kwargs)
        if to_dict:
            inspect = reflection.Inspector.from_engine(self.engine)
            all_colum_name = [colum_info['name'] for colum_info in inspect.get_columns(model_name)]
            for object_ in all_filter_object:
                object_data = {}
                for colum_name in all_colum_name:
                    object_data[colum_name] = getattr(object_, colum_name)
                yield object_data
        else:
            for object_ in all_filter_object:
                yield object_

        session.close()

    def all(self, model_name):
        return self.filter(model_name)

    def execute(self, sql):
        """execute sql statement

        :param str sql: sql statement

        return(tuple): the first element of the tuple is the number of rows affected by the sql statement,
                       if it is a select statement, the second element returns the data,if it is not a  select
                       statement,the second element return null
        """
        session = self.Session()

        try:
            execute_result = session.execute(sql)
        except Exception as e:
            raise ExecuteSqlError('execute sql "%s" failed, %s' % (sql, e))

        # return the data if it is a select statement
        if execute_result.returns_rows:
            ret = execute_result.fetchall()
        else:
            ret = execute_result.rowcount

        session.commit()
        session.close()
        return ret


class StatementStorage:
    def __init__(self, **kwargs):
        database_uri = kwargs.get('database_uri', None)
        self.db = SQLStorage(database_uri=database_uri)
        self._operating_model = kwargs.get('operating_model', 'statement')

    @property
    def operating_model(self):
        return self._operating_model

    @operating_model.setter
    def operating_model(self, new_operating_model):
        self._operating_model = new_operating_model

    def count(self):
        return self.db.count(self.operating_model)

    def delete(self, **kwargs):
        return self.db.delete(self.operating_model, **kwargs)

    def create(self, **kwargs):
        return self.db.create(self.operating_model, **kwargs)

    def filter(self, **kwargs):
        return self.db.filter(self.operating_model, **kwargs)

    def all(self):
        return self.db.filter(self.operating_model)
