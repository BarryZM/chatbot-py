from .adapter import LogicAdapter
from .utils import initialize_class, logger, validate_class, import_module, get_features, get_object_path
from .constants import MAXIMUM_SIMILARITY_THRESHOLD, MINIMUM_SIMILARITY_THRESHOLD, \
    NUMBER_OF_ANSWERS, CONTEXT_PARAMETER_MAX_ERROR_COUNT
from .exceptions import NotEnoughParameterError
from .models import statement_table_name, tag_table_name, tag_association_statement_table_name, access_log_table_name
from .storage import SQLStorage


class ChatBot:
    def __init__(self, name, **kwargs):
        self.name = name
        # storage = kwargs.get('storage', 'chatbot.storage.SQLStorage')
        storage = kwargs.get('storage', SQLStorage())

        # initialize storage class
        if isinstance(storage, str) or isinstance(storage, dict):
            self.storage = initialize_class(storage)
        else:
            self.storage = storage

        # logger
        self.logger = kwargs.get('logger', logger)

        # Stop searching when it is greater than the match
        self.maximum_similarity_threshold = kwargs.get('maximum_similarity_threshold', MAXIMUM_SIMILARITY_THRESHOLD)

        # The minimum amount of similarity between two statement, below this value,
        # the chatbot cannot answer questions from the user.
        self.minimum_similarity_threshold = kwargs.get(
            'minimum_similarity_threshold', MINIMUM_SIMILARITY_THRESHOLD
        )

        # number of answers
        self.number_of_answers = kwargs.get(
            'number_of_answers', NUMBER_OF_ANSWERS
        )

        # Logic adapters used by the chatbot
        adapters = kwargs.get('logic_adapters', [
            {
                'import_path': 'chatbot.adapter.WhatCanIDo',
                'storage': self.storage,
                'logger': self.logger
            },
            {
                'import_path': 'chatbot.adapter.DomainManager',
                'logger': self.logger
            },
            {
                'import_path': 'chatbot.adapter.BestMatch',
                'storage': self.storage,
                'logger': self.logger
            },
        ])

        # initialize the adapter class
        self.logic_adapters = []
        for adapter in adapters:
            validate_class(adapter, LogicAdapter)
            logic_adapter = initialize_class(adapter)
            self.logic_adapters.append(logic_adapter)

        # the processing before the statement is passed to the chatbot
        self.preprocessors = []
        preprocessors = kwargs.get(
            'preprocessors', [
                'chatbot.preprocessor.clean_whitespace'
            ]
        )
        for preprocessor in preprocessors:
            self.preprocessors.append(import_module(preprocessor))

        if kwargs.get('initialize', True):
            self.initialize()

    def initialize(self):
        pass

    def get_response(self, input_statement=None, **kwargs):
        """
        Return the bot's response based on the input.

        :param str input_statement: string
        :returns str: a response to the input
        """
        self.logger.info('the processing the statement "{}"'.format(input_statement))
        # Preprocess the input statement
        for preprocessor in self.preprocessors:
            input_statement = preprocessor(input_statement)
            self.logger.info('after the preprocessor "{}" processing, the statement becomes "{}"'.format(
                get_object_path(preprocessor), input_statement
            ))

        response = {
            'text': '',
            'context': kwargs.get('context', {'domain': False}),
        }
        # matching statements for each adapter
        all_adapter_answers = []
        for adapter in self.logic_adapters:
            if adapter.can_process(input_statement, **kwargs):
                self.logger.info('"{}" adapter starts matching'.format(get_object_path(adapter)))
                answers = adapter.process(input_statement, **kwargs)
                all_adapter_answers.extend(answers)
                self.logger.info('"{}" adapter select "{}" answers'.format(get_object_path(adapter), len(answers)))
                for answer in answers:
                    self.logger.info(
                        '"{}" adapter select the answer to the "{}" question as a reply, the confidence is {}'.format(
                            get_object_path(adapter), answer.reference_question, answer.confidence
                        )
                    )
                    # stop matching
                    if answer.confidence >= self.maximum_similarity_threshold:
                        self.logger.info(
                            'the similarity is {} higher than the {} parameter, stop matching.'.format(
                                answer.confidence, 'maximum_similarity_threshold'
                            )
                        )
                        try:
                            response['text'] = answer.get_answer()
                            response['context'] = {'domain': False}
                            # record access log
                            if answer.id != -1:
                                self.storage.create(model_name=access_log_table_name, statement_id=answer.id)
                        except NotEnoughParameterError as e:
                            if response['context'].get('need_extract_parameter') == e.parameter:
                                error_count = response['context'].get('need_extract_parameter_count', 0) + 1
                            else:
                                error_count = 0

                            if error_count >= CONTEXT_PARAMETER_MAX_ERROR_COUNT:
                                response['text'] = '错误次数过多,该问题已被终止!'
                                response['context']['domain'] = False
                            else:
                                response['text'] = e.message
                                response['context'] = answer.serialize()
                                response['context']['need_extract_parameter'] = e.parameter
                                response['context']['need_extract_parameter_count'] = error_count
                                response['context']['domain'] = True
                        self.logger.info(
                            'finally the response of the "{}" statement is "{}"'.format(input_statement, response)
                        )
                        return response
            else:
                self.logger.info(
                    'not processing the statement using "{}"'.format(get_object_path(adapter))
                )

        all_adapter_answers.sort(key=lambda s: s.confidence, reverse=True)
        all_adapter_answers = all_adapter_answers[:self.number_of_answers]
        if all_adapter_answers:
            response['text'] = '看看这些内容对您有帮助么？\n{}\n都不是？请用一句话完整描述您的问题'.format(
                '\n'.join(['{}.{}'.format(index + 1, answer.reference_question)
                           for index, answer in enumerate(all_adapter_answers)])
            )
        else:
            response['text'] = '很抱歉，没有理解您的意思，请用简短的话描述您的问题，比如"获取主机的磁盘空间使用率？"'

        self.logger.info('finally the response of the "{}" statement is "{}"'.format(
            input_statement, response
        ))

        return response

    def learn(self, question, answer, category='其他', type_=0, parameters=None, extractor=None):
        """
        Learn that the statement provided is a valid response.
        """
        features = get_features(question)
        if not features:
            self.logger.warning('because statement "{}" has no features, so skip learning'.format(question))
            return

        # add data to statement table
        try:
            statement_id = self.storage.create(
                model_name=statement_table_name,
                question=question,
                answer=answer,
                category=category,
                type=type_,
                parameters=parameters,
                extractor=extractor
            )
        except Exception as e:
            self.logger.warning('Inserting data into the database failed, {}'.format(e))
            return

        # add data to tag table and tag_association_statement table
        for feature in features:
            tag = list(self.storage.filter(model_name=tag_table_name, name=feature))
            if len(tag) == 0:
                tag_id = self.storage.create(
                    model_name=tag_table_name,
                    name=feature
                )
            else:
                tag_id = tag[0].id

            self.storage.create(
                model_name=tag_association_statement_table_name,
                tag_id=tag_id,
                statement_id=statement_id
            )

        self.logger.info('add "{}" as the answer to "{}"'.format(
            answer,
            question
        ))
