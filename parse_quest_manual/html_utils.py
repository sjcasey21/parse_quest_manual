import bs4
from itertools import takewhile
from .utils import parse_row


def parse_table(table: bs4.element.Tag):
    head, *rows = table.find_all('tr')
    head = [i.text.strip() for i in head.find_all('td')]
    rows = [[i.text.strip() for i in row.find_all('td')] for row in rows]

    data = [parse_row(dict(zip(head, row))) for row in rows]
    return data


def chunk_categories(start_node):
    nodes = [start_node, *start_node.find_all_next('h3')]
    nodes = [{
        'category':
        node.text.strip().lower(),
        'content': [
            tag for tag in takewhile(
                lambda x: x.name > 'h3',
                node.find_next_siblings(True),
            )
        ],
    } for node in nodes]

    return nodes


def parse_contents(categories):
    def conditional_dict(key, value, func):
        return {key: func(value)} if value else {}

    def tag_to_str(tag):
        return str.lower(str.strip(bs4.element.Tag.getText(tag)))

    return [{
        **category, 'content': [{
            **conditional_dict(
                'type',
                tag.find_previous_sibling('h4'),
                tag_to_str,
            ),
            'items':
            parse_table(tag),
        } for tag in category['content'] if tag.name == 'table']
    } for category in categories]