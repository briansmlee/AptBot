# -*- coding: utf-8 -*-
"""
Python Slack Serializer class for use with the aptbot
"""
# careful about yaml

class Serializer:
    """
    Instanciates a Serializer object to create message attachments.
    """
    def __init__(self):
        pass

    def groups_response(self, groups):
        """ create attachments for all groups """
        pre = '{} groups match your search\n'.format(len(groups))
        result = '\n'.join(['{}\nGroup {}\n{}\n\n'.format('-' * 80, idx, '-' * 80)
                          + self.each_group(group)
                          for idx, (gid, group) in enumerate(groups.items(), 1)])
        return '\n'.join([pre, result])

    def each_group(self, group):
        """ create attachments for all groups """
        return '\n\n'.join(['*{}*:\n{}'.
                           format(k, (v if not isinstance(v, list) else ', '.join(v)))
                           for k, v in group.items()])

    def default_response(self, commands):
        """ default response explaining commands"""
        pre = 'Please use one of the following commands:'
        result = ['*{}*: {}'.format(k, v) for k, v in commands.items()]
        post = 'For example, try \"@aptbot group APT 2\"'
        return '\n'.join([pre, '\n'.join(result), post])


