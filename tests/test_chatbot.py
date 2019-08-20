from chatbot.chatbot import ChatBot
from chatbot.models import statement_table_name
from unittest import TestCase
import os


class ChatBotTest(TestCase):
    @classmethod
    def setUpClass(cls):
        current_file_path = os.path.dirname((os.path.abspath(__file__)))
        db_file_path = os.path.join(current_file_path, 'db.sqlite3')
        if os.path.isfile(db_file_path):
            os.remove(db_file_path)
        cls.bot = ChatBot('test')

    def test_1_learn(self):
        dynamic_statement_data = {
            'question': 'test',
            'answer': 're.split',
            'type_': 1,
            'parameters': 'pattern=:;string=1:2:3:4;',
        }
        self.bot.learn(**dynamic_statement_data)
        self.assertEqual(self.bot.storage.count(statement_table_name), 1)

        static_statement_data = {
            'question': '早上吃鸡蛋对身体好吗',
            'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
        }
        self.bot.learn(**static_statement_data)
        self.assertEqual(self.bot.storage.count(statement_table_name), 2)

    def test_2_get_response(self):
        response = self.bot.get_response('test')
        self.assertEqual(response['text'], ['1', '2', '3', '4'])

        response = self.bot.get_response('早上吃鸡蛋对身体好吗')
        self.assertRegex(response['text'], '早餐当中吃鸡蛋，的确是对身体有很大的益处')

    def test_get_response_domain(self):
        dynamic_statement_data = {
            'question': 'domain test',
            'answer': 're.split',
            'type_': 1,
            'parameters': '',
            'extractor': ''
        }
        self.bot.learn(**dynamic_statement_data)

        aaa = self.bot.get_response('domain test')
        print(aaa)
        bbb = self.bot.get_response(':', **aaa)
        print(bbb)
        ccc = self.bot.get_response('1:2:3', **bbb)
        print(ccc)


# class ChatBotTest111(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.bot = ChatBot(
#             'django',
#             storage={
#                 'import_path': 'chatbot.storage.SQLStorage',
#                 'database_uri': 'mysql+pymysql://root:123456@10.1.196.29:3306/chatbot'
#             }
#         )
#
#     def test_222(self):
#         aaa = self.bot.get_response('磁盘使用率')
#         print(aaa)
#         bbb = self.bot.get_response('10.1.196.52', **aaa)
#         print(bbb)
#         ccc = self.bot.get_response('root', **bbb)
#         print(ccc)
#         ddd = self.bot.get_response('Infra.2019', **ccc)
#         print(ddd)
