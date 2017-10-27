# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
from pprint import pprint
import os
import time
import pickle
from Serializer import Serializer
from slackclient import SlackClient


class Bot:
    """ Instantiates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        self.name = "aptbot"
        self.token = os.environ.get('BOT_TOKEN')
        self.client = SlackClient(self.token)
        self.bot_id = self.get_bot_id()
        self.at_bot = '<@' + self.bot_id + '>'
        self.serializer = Serializer()
        self.commands = {
            'group': 'information about the APT group(s) containing the given name',
            'tool': 'list of APT groups that use the given tool',
            'target': 'list of APT groups that target the given asset or organization',
            'ops': 'list of APT group that executed the given operation'
        }
        path = '../data/'
        with open(path + 'groups.pkl', 'rb') as f:
            self.gid_to_group = pickle.load(f)  # dict of groups
        with open(path + 'command_to_gid.pkl', 'rb') as f:
            self.command_to_gid = pickle.load(f)

    def get_bot_id(self):
        """ gets bot id using token """
        # retrieve bot id
        api_call = self.client.api_call('users.list')
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.name:
                    return user.get('id')

        else:
            print("could not find bot user with the name " + self.name)
            return None

    def handle_command(self, text, channel):
        """
        parses text and handles if valid command
        """
        parsed = text.split(' ', 1)  # command and args (can be None)
        if len(parsed) == 1 and parsed[0] == 'help':  # help command takes no arguments
            response = self.serializer.default_attachment(self.commands)
        elif len(parsed) >= 2 and parsed[0] in self.commands:  # any command with at least one arg
            cmmd, args = parsed[0], parsed[1].split(' ')
            groups = {}
            dct = self.command_to_gid[cmmd]  # get target map
            for key, gid in dct.keys():
                for arg in args:
                    if arg in key and gid not in groups.keys():
                        groups[gid] = self.gid_to_group[gid]

            response = self.serializer.groups_attachment(groups)

        else:  # invalid command
            response = self.default_response()

        # post result as attachment
        post_message = self.client.api_call("chat.postMessage",
                                            channel=channel,
                                            username=self.name,
                                            text='response',
                                            attachments=response
                                            )
        print('message attachment posted!')

    def default_response(self):
        """ returns default response """
        return self.serializer.default_attachment(self.commands)

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.at_bot in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.at_bot)[1].strip(), \
                           output['channel']
        return None, None
    
    def run(self):
        """ runs and processes slack output in a lopp"""
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading

        if self.client.rtm_connect():
            print("APT bot connected and running!")
            while True:
                command, channel = self.parse_slack_output(self.client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
