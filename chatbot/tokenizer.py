import os
import codecs
import jieba.posseg as pseg
import jieba
from .utils import logger
from .constants import PROJECT_DIR_PATH


class Tokenizer:
    def __init__(self, **kwargs):
        stop_word_file_path = kwargs.get('stop_word_file_path',
                                         os.path.join(PROJECT_DIR_PATH, 'data', 'stopwords.txt'))
        self._all_stop_word = list(self.get_stop_word(stop_word_file_path))

        # logger
        self.logger = kwargs.get('logger', logger)

    @staticmethod
    def get_stop_word(file_path):
        with codecs.open(file_path, 'r', encoding='utf8') as f:
            for line in f:
                yield line.strip()


class JiebaTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # load custom dictionary
        custom_dictionary_file_path = kwargs.get('custom_dictionary_file_path',
                                                 os.path.join(PROJECT_DIR_PATH, 'data', 'dict.txt'))
        jieba.load_userdict(custom_dictionary_file_path)

    def cut(self, statement, seg_only=False, remove_stop_word=False):
        segment_statement = []
        if seg_only:
            for word in jieba.cut(statement):
                if remove_stop_word:
                    if word not in self._all_stop_word:
                        segment_statement.append(word)
                else:
                    segment_statement.append(word)
        else:
            for word, tag in pseg.cut(statement):
                if remove_stop_word:
                    if word not in self._all_stop_word:
                        segment_statement.append((word, tag))
                else:
                    segment_statement.append((word, tag))

        return segment_statement


jieba_segment = JiebaTokenizer()
