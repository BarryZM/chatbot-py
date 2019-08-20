from chatbot.preprocessor import clean_whitespace, unescape_html
from unittest import TestCase


class PreprocessorTest(TestCase):
    def test_clean_whitespace(self):
        statement = 'hello,    how are you?  '
        self.assertEqual(clean_whitespace(statement), 'hello, how are you?')

    def test_unescape_html(self):
        statement = (
            'The quick brown fox &lt;b&gt;jumps&lt;/b&gt; over'
            ' the <a href="http://lazy.com">lazy</a> dog.'
        )

        normal_statement = (
            'The quick brown fox <b>jumps</b> over'
            ' the <a href="http://lazy.com">lazy</a> dog.'
        )
        self.assertEqual(unescape_html(statement), normal_statement)
