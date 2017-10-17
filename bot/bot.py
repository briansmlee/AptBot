# by Seungmin Lee
# referenced one of my previous projects NutBot
# and https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

import time
from slackclient import SlackClient
import pickle
from settings import BOT_TOKEN, BOT_ID

class AptBot:
    """ Slack Bot to inform users about APT groups """

    def __init__(self):
        self.AT_BOT = "<@" + BOT_ID + ">"
        self.slack_client = SlackClient(BOT_TOKEN)
        self.commands = {
            'group': 'information about the APT group(s) containing the given name',
            'tool': 'list of APT groups that use the given tool',
            'target': 'list of APT groups that target the given asset or organization',
            'ops': 'list of APT group that executed the given operation'
        }
        self.pkl_path = '../data/APT_dict.pkl'
        with open(self.pkl_path, 'rb') as f:
            self.apt_groups = pickle.load(f)  # dict of groups

        # pprint(self.apt_groups)

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """

        lst = command.split(' ', 1)
        if command.startswith('help'):
            response = self.default_response(True)
        elif len(lst) < 2:
            response = "Please provide at least two arguments. Try \"@aptbot help\""
        else:
            cmmd, args = lst
            if cmmd == 'group':
                response = self.handle_group(args)
            elif cmmd == 'tool':
                response = self.handle_tool(args)
            elif cmmd == 'target':
                response = self.handle_target(args)
            elif cmmd == 'ops':
                response = self.handle_ops(args)
            else:
                response = self.default_response(False)

        self.slack_client.api_call("chat.postMessage",
                                   channel=channel,
                                   text=response,
                                   as_user=True)

    def default_response(self, is_help):
        response = "Not sure what you mean. "
        commands_info = "Please use one of the following commands:\n\n" + \
                        '\n'.join(['{}: {}'.format(k, v) for k, v in self.commands.items()])
        example = '\n\nExample: \"@aptbot group APT 2\"'

        return ('' if is_help else response) + commands_info + example

    def handle_group(self, arg):
        """ returns list of groups with names containing the given string """
        groups = []
        arg_lower = arg.lower()
        for group in self.apt_groups:
            for name in group['names']:
                if arg_lower in name.lower():
                    groups.append(group)

        if groups:
            response = 'The following information is known about the group(s) ' \
                       'with name containing \"{}\":\n'.format(arg)
            groups_info = ''
            for count, group in enumerate(groups, start=1):
                groups_info += '\n----- Match {} -----\n'.format(count)
                groups_info += '\n'.join(['{}:\n{}\n'.format(
                    k, (', '.join(v) if isinstance(v, list) else v)) for k, v in group.items()])

            return response + groups_info

        return "group with name \"{}\" was not found".format(arg)

    def handle_tool(self, arg):
        """ returns list of groups that uses given tool """
        names = []
        arg_lower = arg.lower()
        for group in self.apt_groups:
            if 'tools' in group.keys():
                for tool in group['tools']:
                    if arg_lower in tool.lower() and group['names']:
                        names.append(group['names'][0])

        if names:
            return 'The following groups use tools ' \
                   'with name containing \"{}\":\n{}'.format(arg, ', '.join(names))
        return "group that uses \"{}\" was not found".format(arg)

    def handle_target(self, arg):
        """ returns list of groups with given target """
        names = []
        arg_lower = arg.lower()
        for group in self.apt_groups:
            if 'targets' in group.keys():
                for target in group['targets']:
                    if arg_lower in target.lower() and group['names']:
                        names.append(group['names'][0])

        if names:
            return 'The following groups target assets ' \
                   'with name containing \"{}\": \n{}'.format(arg, ', '.join(names))
        else:
            return 'group that targets \"{}\" was not found'.format(arg)

    def handle_ops(self, arg):
        """ returns list of groups that executed the given operation """
        names = []
        arg_lower = arg.lower()
        for group in self.apt_groups:
            if 'operations' in group.keys():
                for op in group['operations']:
                    if arg_lower in op.lower() and group['names']:
                        names.append(group['names'][0])

        if names:
            return 'The following groups executed an operation ' \
                   'with name containing \"{}\": \n{}'.format(arg, ', '.join(names))
        return 'group that executed the operation \"{}\" was not found'.format(arg)

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.AT_BOT)[1].strip(), \
                           output['channel']
        return None, None

    def run(self):
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

        if self.slack_client.rtm_connect():
            print("APT bot connected and running!")
            while True:
                command, channel = self.parse_slack_output(self.slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

if __name__ == '__main__':
    bot = AptBot()
    bot.run()
