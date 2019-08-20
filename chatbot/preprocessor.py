def clean_whitespace(statement):
    """
    Remove any consecutive whitespace characters from the statement
    """
    import re

    # Replace linebreaks and tabs with spaces
    statement = statement.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # Remove any leeding or trailing whitespace
    statement = statement.strip()

    # Remove consecutive spaces
    statement = re.sub(' +', ' ', statement)

    return statement


def unescape_html(statement):
    """
    Convert escaped html characters into unescaped html characters.
    For example: "&lt;b&gt;" becomes "<b>".
    """
    import html

    statement = html.unescape(statement)

    return statement
