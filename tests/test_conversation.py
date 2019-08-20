from chatbot.conversation import Statement
from unittest import TestCase


class StatementTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dynamic_statement_data = {
            'question': 'test',
            'answer': 're.split',
            'parameters': 'pattern=:;string=1:2:3:4;',
            'type': 1
        }
        cls.dynamic_statement = Statement(**cls.dynamic_statement_data)

        cls.static_statement_data = {
            'question': '早上吃鸡蛋对身体好吗',
            'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
        }
        cls.static_statement = Statement(**cls.static_statement_data)

    def test_get_statement_field_names(self):
        self.assertEqual(self.dynamic_statement.get_statement_field_names(),
                         self.dynamic_statement.statement_field_names)

    def test_serialize(self):
        static_statement_serialize_data = self.static_statement.serialize()
        self.assertEqual(static_statement_serialize_data.get('type'), 0)
        self.assertEqual(static_statement_serialize_data.get('reference_question'), '')
        self.assertEqual(static_statement_serialize_data.get('parameters'), '')
        self.assertEqual(type(static_statement_serialize_data.get('extractor')).__name__, 'Extractor')
        self.assertEqual(static_statement_serialize_data.get('confidence'), 0)
        self.assertEqual(static_statement_serialize_data.get('question'), self.static_statement_data.get('question'))
        self.assertEqual(static_statement_serialize_data.get('answer'), self.static_statement_data.get('answer'))

        dynamic_statement_data = self.dynamic_statement.serialize()
        self.assertEqual(dynamic_statement_data.get('type'), 1)
        self.assertEqual(dynamic_statement_data.get('reference_question'), '')
        self.assertEqual(list(dynamic_statement_data.get('parameters').items()),
                         [('pattern', ':'), ('string', '1:2:3:4'), ('maxsplit', 0), ('flags', 0)])
        self.assertEqual(type(dynamic_statement_data.get('extractor')).__name__, 'Extractor')
        self.assertEqual(dynamic_statement_data.get('confidence'), 0)
        self.assertEqual(dynamic_statement_data.get('question'), self.dynamic_statement_data.get('question'))
        self.assertEqual(dynamic_statement_data.get('answer'), ['1', '2', '3', '4'])
