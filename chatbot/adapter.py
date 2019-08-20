from .utils import logger, initialize_class, get_features, validate_class, import_module, get_object_path
from .extractor import Extractor
from .comparison import levenshtein_distance
from .exceptions import MethodNotImplementedError, ExtractDataError
from .constants import MAXIMUM_SIMILARITY_THRESHOLD, MINIMUM_SIMILARITY_THRESHOLD, NUMBER_OF_ANSWERS
from .storage import SQLStorage
from .conversation import Statement
from .models import statement_table_name, tag_table_name, tag_association_statement_table_name
from .tokenizer import jieba_segment as segment


class LogicAdapter:
    """
    This is an abstract class that represents the interface
    that all logic adapters should implement.

    :param storage:
        storage model
    :param maximum_similarity_threshold:
        The maximum amount of similarity between two statement that is required
        before the search process is halted. The search for a matching statement
        will continue until a statement with a greater than or equal similarity
        is found or the search set is exhausted.
        Defaults to 0.8
    :param default_response:
          The default response returned by this logic adapter
          if there is no other possible response to return.
    :type default_response: str or list or tuple
    """

    def __init__(self, **kwargs):
        storage = kwargs.get('storage', SQLStorage())

        # initialize storage class
        if isinstance(storage, str) or isinstance(storage, dict):
            self.storage = initialize_class(storage)
        else:
            self.storage = storage

        self.maximum_similarity_threshold = kwargs.get(
            'maximum_similarity_threshold', MAXIMUM_SIMILARITY_THRESHOLD
        )

        self.minimum_similarity_threshold = kwargs.get(
            'minimum_similarity_threshold', MINIMUM_SIMILARITY_THRESHOLD
        )

        self.number_of_answers = kwargs.get(
            'number_of_answers', NUMBER_OF_ANSWERS
        )

        self.default_responses = kwargs.get('default_response', [])

        # Convert a single string into a list
        if isinstance(self.default_responses, str):
            self.default_responses = [
                self.default_responses
            ]

        # logger
        self.logger = kwargs.get('logger', logger)

    def can_process(self, statement, **kwargs):
        """
        A preliminary check that is called to determine if a
        logic adapter can process a given statement. By default,
        this method returns true but it can be overridden in
        child classes as needed.

        :rtype: bool
        """
        return True

    def process(self, statement, **kwargs):
        """
        Override this method and implement your logic for selecting a response to an input statement.

        A confidence value and the selected response statement should be returned.
        The confidence value represents a rating of how accurate the logic adapter
        expects the selected response to be. Confidence scores are used to select
        the best response from multiple logic adapters.

        The confidence value should be a number between 0 and 1 where 0 is the
        lowest confidence level and 1 is the highest.

        :param str statement: An input statement to be processed by the logic adapter.

        :return Statement:
        """
        raise MethodNotImplementedError()

    def get_default_response(self, statement):
        """
        This method is called when a logic adapter is unable to generate any
        other meaningful response.
        """
        from random import choice

        if self.default_responses:
            response = Statement(
                question=statement,
                answer=choice(self.default_responses)
            )
        else:
            response = Statement(
                question=statement,
                answer=statement
            )

        # Set confidence to zero because a default response is selected
        response.confidence = 0

        return response

    @property
    def class_name(self):
        """
        Return the name of the current logic adapter class.
        This is typically used for logging and debugging.
        """
        return str(self.__class__.__name__)


class BestMatch(LogicAdapter):
    """
    A logic adapter that returns a response based on known responses to
    the closest matches to the input statement.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Use full library scan when there are no keywords
        self.using_full_library_scan = kwargs.get('using_full_library_scan', False)

        # comparator
        self.comparator = kwargs.get('comparator', levenshtein_distance)

    def can_process(self, statement, **kwargs):
        return not kwargs.get('context', {}).get('domain')

    def process(self, input_statement, **kwargs):
        features = get_features(input_statement)
        if features:
            self.logger.info('the keyword of the "{}" statement is "{}"'.format(
                input_statement, ','.join(['{}'.format(f) for f in features]))
            )
            sql = '''SELECT distinct s.* FROM {statement_table} s, {tag_table} t, {tag_association_statement_table} tas
                   where s.id = tas.statement_id
                   and t.id = tas.tag_id
                   and t.name in ({condition});'''.format(
                statement_table=statement_table_name,
                tag_table=tag_table_name,
                tag_association_statement_table=tag_association_statement_table_name,
                condition=','.join(['"{}"'.format(f) for f in features])
            )
            all_need_to_match_statements = self.storage.execute(sql)

            if not all_need_to_match_statements:
                if self.using_full_library_scan:
                    self.logger.info('unable to find database data using keywords, change to full library comparison')
                    all_need_to_match_statements = self.storage.all(statement_table_name)
                else:
                    self.logger.info('unable to find database data using keywords')
                    return []
            else:
                self.logger.info('use keywords to find "{}" pieces of data and use it for comparison'.format(
                    len(all_need_to_match_statements))
                )
        else:
            if self.using_full_library_scan:
                self.logger.info('"{}" statement has no keywords, full library comparison'.format(input_statement))
                all_need_to_match_statements = self.storage.all(statement_table_name)
            else:
                self.logger.info('"{}" statement has no keywords'.format(input_statement))
                return []

        # get similarity to all data in the database
        all_result = []
        for statement in all_need_to_match_statements:
            similarity = self.comparator(input_statement, statement.question)
            self.logger.debug(
                'the similarity between the statement "{}" and the statement "{}" is {}'.format(
                    input_statement, statement.question, similarity
                )
            )
            if similarity >= self.minimum_similarity_threshold:
                all_result.append(
                    Statement(
                        id=statement.id,
                        question=input_statement,
                        reference_question=statement.question,
                        confidence=similarity,
                        answer=statement.answer,
                        category=statement.category,
                        type=statement.type,
                        parameters=statement.parameters,
                        extractor=statement.extractor
                    )
                )

            # if the similarity is greater than the maximum_similarity_threshold,
            # the matching is stopped, which can reduce the matching time.
            if similarity >= self.maximum_similarity_threshold:
                return [all_result[-1]]

        # get the statement with the highest similarity
        res = []
        if all_result:
            all_result.sort(key=lambda s: s.confidence, reverse=True)
            res = all_result[:self.number_of_answers]
        # else:
        #     res = [self.get_default_response(input_statement)]

        return res


class DomainManager(LogicAdapter):
    def can_process(self, statement, **kwargs):
        return kwargs.get('context', {}).get('domain')

    def process(self, input_statement, **kwargs):
        context = kwargs.get('context', {})
        id_ = context.get('id')
        question = context.get('question')
        reference_question = context.get('reference_question')
        confidence = context.get('confidence')
        answer = context.get('answer')
        category = context.get('category')
        type_ = context.get('type')
        parameters = context.get('parameters')
        need_extract_parameter = context.get('need_extract_parameter')
        extractor = context.get('extractor')

        # initial extractor
        validate_class(extractor, Extractor)
        extractor_obj = import_module(extractor)(input_statement)

        # extract parameter
        get_arg_val_fun = getattr(extractor_obj, 'extract_{}'.format(need_extract_parameter),
                                  None) or getattr(extractor_obj, 'extract_general')
        self.logger.info(
            'get the value of the "{}" parameter using "{}" method'.format(
                need_extract_parameter, get_object_path(get_arg_val_fun)
            )
        )
        try:
            argument_value = get_arg_val_fun()
            parameters[need_extract_parameter] = argument_value
            self.logger.info('the value is "{}"'.format(argument_value))
        except ExtractDataError:
            self.logger.error(
                'The "{}" method can not get the value of the "{}" parameter from the context "{}".'.format(
                    get_object_path(get_arg_val_fun),
                    need_extract_parameter,
                    input_statement
                )
            )

        return [
            Statement(
                id=id_,
                question=question,
                reference_question=reference_question,
                confidence=confidence,
                answer=answer,
                category=category,
                type=type_,
                parameters=parameters,
                extractor=extractor
            )
        ]


class WhatCanIDo(LogicAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # comparator
        self.comparator = kwargs.get('comparator', levenshtein_distance)

    def can_process(self, statement, **kwargs):
        if not kwargs.get('context', {}).get('domain'):
            segment_text = segment.cut(statement, seg_only=True, remove_stop_word=True)
            for keyword in ['功能', '能力']:
                if keyword in segment_text:
                    return True

    def process(self, input_statement, **kwargs):
        questions = ['机器人功能', '机器人能力']
        for question in questions:
            similarity = self.comparator(input_statement, question)
            if similarity >= self.maximum_similarity_threshold:
                answer = '我提供的服务如下:\n'
                index = 0
                for dynamic_qa in self.storage.filter(statement_table_name, type=1):
                    index += 1
                    answer += '{}. {}\n'.format(index, dynamic_qa.question)

                answer += '{}. 我的大脑还植入了{}条与电脑有关的知识,你可以问我关于这方面的问题\n'.format(
                    index + 1,
                    self.storage.count(statement_table_name) - index
                )
                return [
                    Statement(
                        id=-1,
                        question=input_statement,
                        reference_question=question,
                        confidence=similarity,
                        answer=answer,
                        category='',
                        type=0,
                        parameters='',
                        extractor=''
                    )
                ]

        return []
