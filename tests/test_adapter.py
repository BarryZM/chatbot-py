import os
from chatbot.adapter import LogicAdapter, BestMatch
from chatbot.exceptions import MethodNotImplementedError
from unittest import TestCase


class LogicAdapterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = LogicAdapter()

    def test_class_name(self):
        self.assertEqual(self.adapter.class_name, 'LogicAdapter')

    def test_can_process(self):
        self.assertTrue(self.adapter.can_process(''))

    def test_process(self):
        with self.assertRaises(MethodNotImplementedError):
            self.adapter.process('')

    def test_get_default_response(self):
        response = self.adapter.get_default_response('测试')
        self.assertEqual(response.answer, '测试')


class BestMatchTest(TestCase):
    """
    Unit tests for the BestMatch logic adapter.
    """
    @classmethod
    def setUpClass(cls):
        current_file_path = os.path.dirname((os.path.abspath(__file__)))
        db_name = 'adapter_test.sqlite3'
        db_file_path = os.path.join(current_file_path, db_name)
        if os.path.isfile(db_file_path):
            os.remove(db_file_path)
        cls.adapter = BestMatch(
            storage={
                'import_path': 'chatbot.storage.SQLStorage',
                'database_uri': 'sqlite:///{}'.format(db_name)
            },
            using_full_library_scan=True
        )

    def test_1_storage_no_data(self):
        model_name = 'statement'
        self.assertEqual(self.adapter.storage.count(model_name), 0)
        statement = '今天天气如何?'
        response = self.adapter.process(statement)

        self.assertEqual(response, [])

    def test_2_storage_have_data(self):
        model_name = 'statement'
        new_statement = {
            'question': '今天天气如何?',
            'answer': '今天阳光明媚,晴空万里'
        }
        self.adapter.storage.create(model_name, **new_statement)

        response = self.adapter.process(new_statement['question'])[0]
        self.assertEqual(response.question, new_statement['question'])
        self.assertEqual(response.answer, new_statement['answer'])
        self.assertEqual(response.confidence, 1)
        self.adapter.storage.delete(model_name, **new_statement)
