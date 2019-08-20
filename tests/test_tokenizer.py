from unittest import TestCase
from chatbot.tokenizer import Tokenizer, JiebaTokenizer


class TokenizerTest(TestCase):
    def test_tokenizer_get_stop_word(self):
        tokenizer = Tokenizer()
        self.assertIn('的', tokenizer._all_stop_word)

    def test_jieba_tokenizer_cut(self):
        jieba_tokenizer = JiebaTokenizer()
        statement = '我爱北京天安门'
        res = jieba_tokenizer.cut(statement, seg_only=True, remove_stop_word=False)
        self.assertEqual(res, ['我', '爱', '北京', '天安门'])

        res = jieba_tokenizer.cut(statement, seg_only=True, remove_stop_word=True)
        self.assertEqual(res, ['爱', '北京', '天安门'])

        res = jieba_tokenizer.cut(statement, seg_only=False, remove_stop_word=False)
        self.assertEqual(res, [('我', 'r'), ('爱', 'v'), ('北京', 'ns'), ('天安门', 'ns')])

        res = jieba_tokenizer.cut(statement, seg_only=False, remove_stop_word=True)
        self.assertEqual(res, [('爱', 'v'), ('北京', 'ns'), ('天安门', 'ns')])

