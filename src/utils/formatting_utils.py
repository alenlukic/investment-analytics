from src.utils.math_utils import is_close_to_zero


def format_currency(decimal):
    """ Formats input decimal as currency string.

    :param decimal: input decimal to format.
    :return: decimal formatted as currency.
    """
    return '$ ' + format_decimal(decimal, 2)


def format_decimal(decimal, n=3):
    """ Formats input decimal as a string.

    :param decimal: input exponent to format.
    :param n: number of decimal places.
    :return: formatted decimal (n decimal places).
    """

    if decimal is None:
        return '(N/A)'

    # Actually an exponent, use different formatting function
    if 'e' in str(decimal):
        return format_exponent(decimal)

    format_prefix = '{0:.' + str(n) + 'f}'

    return format_prefix.format(0 if is_close_to_zero(decimal) else decimal)


def format_exponent(exponent):
    """ Formats input exponent as a string.

    :param exponent: input exponent to format.
    :return: formatted exponent (3 decimal places).
    """
    return '{0:.3e}'.format(exponent)


def format_rank(num):
    """ Takes an input number and returns a formatted rank string (e.g. 1 -> "1st", 23 -> "23rd").

    :param num: number to format as a rank.
    :return: formatted rank string.
    """

    rank = str(num)
    suffix = 'th'

    if rank[-1] == '1':
        suffix = 'st'
    if rank[-1] == '2':
        suffix = 'nd'
    if rank[-1] == '3':
        suffix = 'rd'
    if len(rank) > 1 and rank[-2] == '1':
        suffix = 'th'

    return rank + suffix
