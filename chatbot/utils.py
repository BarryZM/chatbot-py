import importlib
import inspect
import logging
import sys
import os
import re
import collections
import jieba.analyse
from .exceptions import InvalidTypeError
from .constants import PROJECT_DIR_PATH, LOG_FILE_NAME, LOG_LEVEL, APP_NAME


def import_module(dotted_path='re.search'):
    """
    Imports the specified module based on the
    dot notated import path for the module.
    """
    module_parts = dotted_path.split('.')
    module_path = '.'.join(module_parts[:-1])
    module = importlib.import_module(module_path)

    return getattr(module, module_parts[-1])


def initialize_class(data, *args, **kwargs):
    """
    :param data: A string or dictionary containing a import_path attribute.
    """
    if isinstance(data, dict):
        import_path = data.pop('import_path')
        kwargs.update(data)
        class_ = import_module(import_path)
    else:
        class_ = import_module(data)

    return class_(*args, **kwargs)


def validate_class(need_validate_class, class_):
    """
    Raises an exception if validate_class is not a
    subclass of adapter_class.

    :param str need_validate_class: The class to be validated.
    :param class class_: The class type to check against.


    :raise: InvalidTypeException
    """
    # If a dictionary was passed in, check if it has an import_path attribute
    if isinstance(need_validate_class, dict):
        if 'import_path' not in need_validate_class:
            raise InvalidTypeError(
                'The dictionary {} must contain a value for "import_path"'.format(
                    str(need_validate_class)
                )
            )

        # Set the class to the import path for the next check
        need_validate_class = need_validate_class.get('import_path')

    if not issubclass(import_module(need_validate_class), class_):
        raise InvalidTypeError(
            '{} must be a subclass of {}'.format(
                need_validate_class,
                class_.__name__
            )
        )


def get_function_arguments(fun):
    arguments = inspect.getfullargspec(fun)[0] or []
    defaults = inspect.getfullargspec(fun)[3] or ()
    args_len = len(arguments)
    defaults_len = len(defaults)

    # if it is a class method, then the self parameter is removed
    if 'self' in arguments:
        arguments.remove('self')

    all_argument_and_value = collections.OrderedDict()
    # all parameters without default values
    for argument in arguments[:(args_len-defaults_len)]:
        all_argument_and_value[argument] = None

    # all parameters with default values
    for argument, argument_default_value in zip(arguments[(args_len-defaults_len):], defaults):
        all_argument_and_value[argument] = argument_default_value

    return all_argument_and_value


def get_features(
        content,
        allow_pos=()):
    stop_word_file_path = os.path.join(PROJECT_DIR_PATH, 'data', 'stopwords.txt')
    jieba.analyse.set_stop_words(stop_word_file_path)
    # keyWord = jieba.analyse.textrank(content, topK=3, allowPOS=['ns', 'n', 'vn', 'v', 'nr'])
    return jieba.analyse.extract_tags(content, topK=max(3, int(len(content) / 6)), allowPOS=allow_pos)


def get_logger(name,
               level=logging.INFO,
               output_stream=sys.stdout,
               log_format='%(asctime)s [%(name)s] [%(filename)s:%(lineno)d] [%(levelname)s] [%(thread)d]: %(message)s'):
    """A function which writes formatted logging records to standard output or standard error output

    :rtype:
    :param str name: log name
    :param int level: Log level
    :param str output_stream: stream output
    :param str log_format: set the log format

    :return(class 'logging.Logger'): logging.Logger
    """
    # create logger
    logger_ = logging.getLogger(name)
    logger_.setLevel(level)

    # create handler
    screen_handler = logging.StreamHandler(stream=output_stream)
    file_handler = logging.FileHandler(
        os.path.join(PROJECT_DIR_PATH, 'log', LOG_FILE_NAME),
        mode='w',
        encoding='utf8'
    )
    # handler = logging.FileHandler(name, 'a', encoding='utf-8')
    screen_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))
    file_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))

    # add handler to logger
    logger_.addHandler(screen_handler)
    logger_.addHandler(file_handler)

    return logger_


logger = get_logger(APP_NAME, LOG_LEVEL)


def get_object_path(object_):
    module_name = inspect.getmodule(object_).__name__
    if inspect.isclass(object_) or inspect.isfunction(object_):
        return '{}.{}'.format(module_name, object_.__name__)
    elif inspect.ismethod(object_):
        return '{}.{}.{}'.format(module_name, object_.__self__.__class__.__name__, object_.__name__)
    else:
        path = module_name
        if hasattr(object_, '__class__'):
            path += '.' + object_.__class__.__name__

        if hasattr(object_, '__name__'):
            path += '.' + object_.__name__

        return path


def get_function_parameter_desc(fun):
    """Get the parameter description in the function"""
    all_parameter_desc = {}
    function_doc = inspect.getdoc(fun)
    if function_doc:
        for line in function_doc.split('\n'):
            line = line.strip()
            if line.startswith(':param'):
                parameter, desc = re.search(r':param\s+.*?(\S+):(.*)', line).groups()
                all_parameter_desc[parameter] = desc.strip()

    return all_parameter_desc


def echo(string):
    print(string)
