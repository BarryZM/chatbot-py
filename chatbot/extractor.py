import re
# import inspect
import jieba
from .tokenizer import jieba_segment as segment
from .exceptions import ExtractDataError
from .utils import logger


class Extractor:
    def __init__(self, text, **kwargs):
        self._text = text
        # logger
        self.logger = kwargs.get('logger', logger)

    def __str__(self):
        return self.__class__.__name__

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @staticmethod
    def _add_word_to_jieba(word_list):
        for word in word_list:
            jieba.add_word(word)

    @staticmethod
    def _del_word_from_jieba(word_list):
        for word in word_list:
            jieba.del_word(word)

    def extract(self,
                key,
                expected_value_pattern=r'[^\u4e00-\u9fff]+',
                tags=('eng', 'n', 'nr', 'ns', 'nt', 'nw', 'nz', 'vn', 'x')):
        """extract data

        :param tuple key: keyword
        :param str expected_value_pattern: expect pattern， The default is non-Chinese
        :param tuple tags: part of speech
        :return str:

        Example:

        ex = Extractor('获取ip地址为1.1.1.1的主机的磁盘空间使用率')
        ip1 = ex.extract(key=('ip地址', 'ip'), expected_value_pattern=r'([0-9]{1,3}.){3}[0-9]{1,3}')
        ex.text = '获取1.1.1.1主机的磁盘空间使用率'
        ip2 = ex.extract(key=('主机', 'ip地址', 'ip'), expected_value_pattern=r'([0-9]{1,3}.){3}[0-9]{1,3}')
        print(ip1, ip2)
        """
        # add word to jieba
        self._add_word_to_jieba(key)

        # segment
        segment_text = segment.cut(self.text, seg_only=False, remove_stop_word=True)
        self.logger.debug('"{}" statement after the word segmentation is "{}"'.format(self.text, segment_text))
        key_index = -1
        for index, word_and_tag in enumerate(segment_text):
            if word_and_tag[0] in key:
                key_index = index
                break

        if key_index != -1:
            the_word_index_before_keyword = key_index - 1
            the_word_index_after_keyword = key_index + 1
            if the_word_index_before_keyword >= 0 and \
                    re.match(expected_value_pattern + r'$', segment_text[the_word_index_before_keyword][0]) and \
                    segment_text[the_word_index_before_keyword][1] in tags:
                return segment_text[the_word_index_before_keyword][0]

            if the_word_index_after_keyword < len(segment_text) and \
                    re.match(expected_value_pattern + r'$', segment_text[the_word_index_after_keyword][0]) and \
                    segment_text[the_word_index_after_keyword][1] in tags:
                return segment_text[the_word_index_after_keyword][0]

        raise ExtractDataError(key[0])

    def extract_general(self):
        return self.text.strip()


class HostExtractor(Extractor):
    def extract_ip(self):
        try:
            ip = self.extract(
                key=('ip地址', 'ip'), expected_value_pattern=r'(\d{1,3}\.){3}\d{1,3}', tags=('m',)
            )
        except ExtractDataError as e:
            ip_match = re.search(r'(\d{1,3}\.){3}\d{1,3}', self.text)
            if ip_match:
                ip = ip_match.group()
            else:
                raise e
        return ip

    def extract_username(self):
        try:
            username = self.extract(
                key=('用户名', '用户', 'username', 'user'), expected_value_pattern=r'[^\u4e00-\u9fff]+'
            )
        except ExtractDataError as e:
            username_match = re.search(r'[^\u4e00-\u9fff]+', self.text)
            if username_match:
                username = username_match.group()
            else:
                raise e
        return username

    def extract_password(self):
        try:
            password = self.extract(
                key=('密码', 'password'), expected_value_pattern=r'[^\u4e00-\u9fff]+'
            )
        except ExtractDataError as e:
            password_match = re.search(r'[^\u4e00-\u9fff]+', self.text)
            if password_match:
                password = password_match.group()
            else:
                raise e
        return password


class WeatherExtractor(Extractor):
    def extract_address(self):
        try:
            address = self.extract(
                key=('地址', 'address'), expected_value_pattern=r'[\u4e00-\u9fff]+'
            )
        except ExtractDataError as e:
            address_match = re.search(r'[\u4e00-\u9fff]+', self.text)
            if address_match:
                address = address_match.group()
            else:
                raise e
        return address

    def extract_day(self):
        try:
            day = self.extract(
                key=('时间', '日期', 'day'), expected_value_pattern=r'\d{8}'
            )
        except ExtractDataError as e:
            day_match = re.search(r'\d{8}', self.text)
            if day_match:
                day = day_match.group()
            else:
                raise e
        return day
