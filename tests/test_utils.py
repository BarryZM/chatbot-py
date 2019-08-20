from unittest import TestCase
from chatbot.utils import import_module, initialize_class, get_function_arguments, \
    logger, get_object_path, get_function_parameter_desc
from chatbot.storage import SQLStorage
import re


class UtilityTest(TestCase):
    def test_import_module(self):
        datetime = import_module('datetime.datetime')
        self.assertTrue(hasattr(datetime, 'now'))

    def test_initialize_class(self):
        res = initialize_class('re.split', pattern=r':', string='a:b')
        self.assertEqual(res, ['a', 'b'])

        res = initialize_class(
            {
                'import_path': 're.split',
                'pattern': r':',
                'string': 'a:b'
            }
        )
        self.assertEqual(res, ['a', 'b'])

    def test_get_function_arguments(self):
        fun_args = get_function_arguments(re.split)
        self.assertEqual(
            list(fun_args.items()), [('pattern', None), ('string', None), ('maxsplit', 0), ('flags', 0)]
        )

    def test_logger(self):
        from logging import Logger
        self.assertIsInstance(logger, Logger)

    def test_get_object_path(self):
        # test class path
        self.assertEqual(get_object_path(TestCase), 'unittest.case.TestCase')

        # test function path
        self.assertEqual(get_object_path(re.split), 're.split')

        # test method
        storage = SQLStorage()
        self.assertEqual(get_object_path(storage.count), 'chatbot.storage.SQLStorage.count')

    def test_get_function_parameter_desc(self):
        def test(string):
            """

            :param string: string desc
            :return:
            """
            pass

        fun_parameter_desc = get_function_parameter_desc(test)
        self.assertEqual(fun_parameter_desc['string'], 'string desc')
