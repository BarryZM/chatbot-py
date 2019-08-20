from .utils import import_module, get_function_arguments, logger, get_function_parameter_desc, get_object_path
from .exceptions import NotEnoughParameterError


class StatementMixin:
    """
    This class has shared methods used to
    normalize different statement models.
    """

    statement_field_names = [
        'id',
        'question',
        'reference_question',
        'confidence',
        'answer',
        'category',
        'type',
        'parameters',
        'extractor',
    ]

    def get_statement_field_names(self):
        """
        Return the list of field names for the statement.
        """
        return self.statement_field_names

    def serialize(self):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}

        for field_name in self.get_statement_field_names():
            # field_method = getattr(self, 'get_{}'.format(
            #     field_name
            # ), None)
            #
            # if field_method:
            #     data[field_name] = field_method()
            # else:
            data[field_name] = getattr(self, field_name)

        return data


class Statement(StatementMixin):
    """
    A statement represents a single spoken entity, sentence or
    phrase that someone can say.
    """
    def __init__(self, question, answer=None, **kwargs):
        self.question = str(question)
        self.answer = answer
        self.id = kwargs.get('id', -1)
        self.reference_question = kwargs.get('reference_question', '')
        self.category = kwargs.get('category', '其他')

        # statement type, if the type is 0, answer = answer, if it is 1, then answer = answer(**parameters)
        self.type = kwargs.get('type', 0)

        # get parameter
        parameters = kwargs.get('parameters', {})
        if self.type == 1:
            self.answer_fun = import_module(self.answer)
            self.parameters = get_function_arguments(self.answer_fun)
            if isinstance(parameters, str):
                for parameter in parameters.split(';'):
                    if parameter.strip():
                        name, value = parameter.strip().split('=')
                        if name.strip() in self.parameters:
                            self.parameters[name.strip()] = value.strip()
            elif hasattr(parameters, 'items'):
                for name, value in getattr(parameters, 'items')():
                    if name in self.parameters:
                        self.parameters[name] = value
        else:
            self.parameters = parameters

        # get extractor
        self.extractor = kwargs.get('extractor', 'chatbot.extractor.Extractor') or 'chatbot.extractor.Extractor'

        # This is the confidence with which the chat bot believes
        # this is an accurate answer. This value is set when the
        # statement is returned by the chat bot.
        self.confidence = kwargs.get('confidence', 0)

        # logger
        self.logger = kwargs.get('logger', logger)

    def __str__(self):
        return self.question

    def __repr__(self):
        return '<Statement text:%s>' % self.question

    def get_answer(self):
        if self.type == 0:
            return self.answer
        elif self.type == 1:
            for parameter, value in self.parameters.items():
                if value is None:
                    parameter_desc = get_function_parameter_desc(self.answer_fun).get(parameter, parameter)
                    raise NotEnoughParameterError(parameter, parameter_desc)
            try:
                self.logger.info('Call the function "{}" to get the answer, all the parameters of the '
                                 'function are "{}"'.format(get_object_path(self.answer_fun), self.parameters))
                text = self.answer_fun(**self.parameters)
            except Exception as e:
                text = str(e)
            return text
