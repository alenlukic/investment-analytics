from src.utils.formatting_utils import format_decimal


class RankFactor:
    """ Utility class that encapsulates a column in a ranking table. """

    def __init__(self, name, priority, format_function=format_decimal):
        """ Constructor.

        :param name: column name.
        :param priority: column sort priority.
        :param format_function: function to use when formatting this factor.
        """
        self.name = name
        self.priority = priority
        self.format_function = format_function

    def format_function(self):
        return self.format_function

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority
