from src.utils.math_utils import is_close_to_zero


def format_decimal(decimal):
    if decimal is None:
        return 'N/A'

    if 'e' in str(decimal):
        return format_exponent(decimal)

    if is_close_to_zero(decimal):
        return '0'

    return '{0:.3f}'.format(decimal)


def format_exponent(exponent):
    return '{0:.3e}'.format(exponent)


def format_rank(rank):
    str_rank = str(rank)
    suffix = 'th'

    if str_rank[-1] == '1':
        suffix = 'st'
    if str_rank[-1] == '2':
        suffix = 'nd'
    if str_rank[-1] == '3':
        suffix = 'rd'
    if len(str_rank) > 1 and str_rank[-2] == '1':
        suffix = 'th'

    return ' (' + str_rank + suffix + ')'
