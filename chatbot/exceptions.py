class ChatbotError(Exception):
    """
    chatbot base error
    """


class InvalidTypeError(ChatbotError):
    """
    An exception to be raised when an adapter
    of an unexpected class type is received.
    """
    pass


class MethodNotImplementedError(NotImplementedError, ChatbotError):
    """
    An exception to be raised when an extractor method has not been implemented.
    Typically this indicates that the developer is expected to implement the
    method in a subclass.
    """

    def __init__(self, message='This method must be overridden in a subclass method.'):
        """
        Set the message for the exception.
        """
        self.message = message
        super().__init__(message)


class ExtractDataError(ChatbotError):
    """
    An exception to be raised when the extractor cannot extract the parameter value
    """

    def __init__(self, parameter_name):
        """
        Set the message for the exception.
        """
        # current_method_name = inspect.stack()[1][3]
        self.parameter = parameter_name
        self.message = 'unable to extract {} data'.format(parameter_name)
        super().__init__(self.message)


class NotEnoughParameterError(ChatbotError):
    def __init__(self, parameter_name, message=None):
        self.parameter = parameter_name
        if message:
            self.message = '请提供{}'.format(message)
        else:
            self.message = '请提供{}参数的值'.format(parameter_name)
        super().__init__(self.message)


class NotFoundExtractorMethod(ChatbotError):
    def __init__(self, method):
        self.message = 'The "{}" method does not exist.'.format(method)
        super().__init__(self.message)


class StorageError(ChatbotError):
    """"""


class ModelNotExistError(StorageError):
    """
    An exception to be raised when the model does not exist in the database
    """

    def __init__(self, model_name):
        """
        Set the message for the exception.
        """
        self.message = 'the "{}" model does not exist in the database'.format(model_name)
        super().__init__(self.message)


class DeleteDataWithoutConditionError(StorageError):
    """
    An exception to be raised when deleting database data does not provide conditions
    """

    def __init__(self, message='deleting database data does not provide conditions'):
        """
        Set the message for the exception.
        """
        self.message = message
        super().__init__(message)


class UniqueError(StorageError):
    def __init__(self, message='line already exists, violates uniqueness constraint'):
        """
        Set the message for the exception.
        """
        self.message = message
        super().__init__(message)


class ExecuteSqlError(StorageError):
    def __init__(self, message='line already exists, violates uniqueness constraint'):
        """
        Set the message for the exception.
        """
        self.message = message
        super().__init__(message)
