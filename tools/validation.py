from lxml import etree
from io import StringIO
from cssselect.parser import SelectorError
from cssselect.xpath import HTMLTranslator


def valid_xpath_expression(xpath):
    """
    检查xpath合法性
    :param xpath:
    :return:
    """
    tree = etree.parse(StringIO('<foo><bar></bar></foo>'))
    try:
        tree.xpath(xpath)
        return True
    except etree.XPathEvalError as e:
        return False


def valid_css_expression(css):
    """
    检查css合法性
    :param css:
    :return:
    """
    try:
        HTMLTranslator().css_to_xpath(css)
        return True
    except SelectorError as e:
        return False
