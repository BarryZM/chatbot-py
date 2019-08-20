from chatbot.comparison import LevenshteinDistance
from unittest import TestCase


class LevenshteinDistanceTest(TestCase):
    def setUp(self):
        self.compare = LevenshteinDistance()

    def test_compare_statement_false(self):
        """
        Falsy values should match by zero.
        """
        statement = ''
        other_statement = '测试'
        value = self.compare(statement, other_statement)
        self.assertEqual(value, 0)

        value = self.compare(other_statement, statement)
        self.assertEqual(value, 0)

    def test_compare_with_same_statement(self):
        statement = '早上吃鸡蛋对身体好吗?'
        other_statement = '早上吃鸡蛋对身体好吗?'
        value = self.compare(statement, other_statement)
        self.assertEqual(value, 1)

    def test_compare_with_different_statement(self):
        statement = '早上吃鸡蛋对身体好吗?'
        other_statement = '今天下暴雨'
        value = self.compare(statement, other_statement)
        self.assertEqual(value, 0)

        statement = '早上吃鸡蛋对身体好吗?'
        other_statement = '早上不吃饭对胃不好'
        value = self.compare(statement, other_statement)
        self.assertLess(value, 1)
        self.assertGreater(value, 0)

