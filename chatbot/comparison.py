from .tokenizer import jieba_segment as segment
from difflib import SequenceMatcher


class Comparator:
    def __call__(self, statement_a, statement_b):
        return self.compare(statement_a, statement_b)

    @staticmethod
    def _cut_statement(statement):
        return segment.cut(statement, seg_only=True)

    def compare(self, statement_a, statement_b):
        return 0


class LevenshteinDistance(Comparator):
    """
    Compare two statements based on the Levenshtein distance
    of each statement.
    """

    def compare(self, statement, other_statement):
        """
        Compare the two input statements.

        :return float: The percent of similarity between the text of the statements.
        """

        # Return 0 if either statement has a falsy text value
        if not statement or not other_statement:
            return 0

        similarity = SequenceMatcher(
            None,
            statement,
            other_statement
        )

        # Calculate a decimal percent of the similarity
        percent = round(similarity.ratio(), 2)

        return percent


levenshtein_distance = LevenshteinDistance()
