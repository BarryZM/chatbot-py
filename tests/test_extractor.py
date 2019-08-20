from chatbot.extractor import Extractor
from unittest import TestCase


class ExtractorTest(TestCase):
    def test_extract(self):
        ex = Extractor('获取ip地址为1.1.1.1的主机的磁盘空间使用率')
        ip = ex.extract(key=('ip地址', 'ip'), expected_value_pattern=r'(\d{1,3}\.){3}\d{1,3}', tags=('m',))
        self.assertEqual(ip, '1.1.1.1')

        ex.text = '获取1.1.1.1主机的磁盘空间使用率'
        ip = ex.extract(key=('主机', 'ip地址', 'ip'), expected_value_pattern=r'(\d{1,3}\.){3}\d{1,3}', tags=('m',))
        self.assertEqual(ip, '1.1.1.1')

    def test_extract_general(self):
        ex = Extractor('  1.1.1.1  ')
        self.assertEqual(ex.extract_general(), '1.1.1.1')