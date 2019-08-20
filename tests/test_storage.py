import os
from unittest import TestCase
from chatbot.storage import SQLStorage, StatementStorage
from chatbot.models import Statement, Tag, TagAssociationStatement, AccessLog
from chatbot.exceptions import ModelNotExistError, DeleteDataWithoutConditionError


current_file_path = os.path.dirname((os.path.abspath(__file__)))


class SQLStorageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        db_name = 'sql_storage_test.sqlite3'
        db_file_path = os.path.join(current_file_path, db_name)
        if os.path.isfile(db_file_path):
            os.remove(db_file_path)
        cls.storage = SQLStorage(database_uri='sqlite:///{}'.format(db_name))

    def test_set_database_uri_none(self):
        storage = SQLStorage(database_uri=None)
        self.assertEqual(storage.database_uri, 'sqlite:///db.sqlite3')

    def test_get_model(self):
        model = self.storage.get_model('statement')
        self.assertEqual(model, Statement)

    def test_get_statement_model(self):
        self.assertEqual(self.storage.get_statement_model(), Statement)

    def test_get_tag_model(self):
        self.assertEqual(self.storage.get_tag_model(), Tag)

    def test_get_tag_association_statement_model(self):
        self.assertEqual(self.storage.get_tag_association_statement_model(), TagAssociationStatement)

    def test_get_access_log_model(self):
        self.assertEqual(self.storage.get_access_log_model(), AccessLog)

    def test_get_model_not_exist_model(self):
        with self.assertRaises(ModelNotExistError):
            self.storage.get_model('statement2')

    def test_count(self):
        model_name = 'statement'
        count = self.storage.count(model_name)
        self.assertEqual(count, 0)

    def test_create_and_delete(self):
        model_name = 'statement'
        new_statement = {
            'question': '早上吃鸡蛋对身体好吗',
            'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
        }
        self.storage.create(model_name, **new_statement)
        self.assertEqual(self.storage.count(model_name), 1)

        condition = {
            'question': '早上吃鸡蛋对身体好吗'
        }
        self.storage.delete(model_name, **condition)
        self.assertEqual(self.storage.count(model_name), 0)

    def test_delete_without_condition(self):
        model_name = 'statement'
        with self.assertRaises(DeleteDataWithoutConditionError):
            self.storage.delete(model_name)

    def test_filter(self):
        model_name = 'statement'
        for i in range(10):
            new_statement = {
                'question': '早上吃鸡蛋对身体好吗{}'.format(i),
                'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
            }
            self.storage.create(model_name, **new_statement)
        self.assertEqual(self.storage.count(model_name), 10)

        condition = {
            'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处'
        }
        for statement in self.storage.filter(model_name, **condition):
            self.assertEqual(statement.question[:-1], '早上吃鸡蛋对身体好吗')
            self.assertEqual(statement.answer, '早餐当中吃鸡蛋，的确是对身体有很大的益处')
        self.storage.delete(model_name, **condition)

    def test_execute(self):
        # test insert
        model_name = 'statement'
        insert_sql = 'insert into statement(question, answer) values("{}", "{}")'.format('q1', 'a1')
        insert_count = self.storage.execute(insert_sql)
        self.assertEqual(insert_count, 1)

        insert_sql = 'insert into statement(question, answer) values("{}", "{}")'.format('q2', 'a2')
        insert_count = self.storage.execute(insert_sql)
        self.assertEqual(insert_count, 1)
        self.assertEqual(self.storage.count(model_name), 2)

        # test select
        select_sql = 'select *  from statement'
        select_data = self.storage.execute(select_sql)
        self.assertEqual(len(select_data), 2)

        # test delete
        delete_sql = 'delete from statement'
        delete_count = self.storage.execute(delete_sql)
        self.assertEqual(delete_count, 2)
        self.assertEqual(self.storage.count(model_name), 0)


class StatementStorageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        db_name = 'statement_storage_test.sqlite3'
        db_file_path = os.path.join(current_file_path, db_name)
        if os.path.isfile(db_file_path):
            os.remove(db_file_path)
        cls.statement_storage = StatementStorage(database_uri='sqlite:///{}'.format(db_name))

    def test_count(self):
        count = self.statement_storage.count()
        self.assertEqual(count, 0)

    def test_create_and_delete(self):
        new_statement = {
            'question': '早上吃鸡蛋对身体好吗',
            'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
        }
        self.statement_storage.create(**new_statement)
        self.assertEqual(self.statement_storage.count(), 1)

        condition = {
            'question': '早上吃鸡蛋对身体好吗'
        }
        self.statement_storage.delete(**condition)
        self.assertEqual(self.statement_storage.count(), 0)

    def test_filter(self):
        for i in range(10):
            new_statement = {
                'question': '早上吃鸡蛋对身体好吗{}'.format(i),
                'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
            }
            self.statement_storage.create(**new_statement)
        self.assertEqual(self.statement_storage.count(), 10)

        condition = {
            'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处'
        }
        for statement in self.statement_storage.filter(**condition):
            self.assertEqual(statement.question[:-1], '早上吃鸡蛋对身体好吗')
            self.assertEqual(statement.answer, '早餐当中吃鸡蛋，的确是对身体有很大的益处')
        self.statement_storage.delete(**condition)
