# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
from pprint import pprint
import os
import pickle
from Serializer import Serializer
from slackclient import SlackClient

# authorized teams. save this in a more persistent memory store.
authed_teams = {}


class Bot:
    """ Instantiates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        # super(Bot, self).__init__()
        self.name = "aptbot"
        self.emoji = ":robot_face:"
        # app credentials from local env
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # scope for limiting permissions for app
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        self.serializer = Serializer()
        self.at_bot = "<@" + self.oauth['client_id'] + ">"  # check
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

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.
        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token
        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # keep track of authorized teams and their associated OAuth tokens
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then reconnect to the Slack Client with the correct team's bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def handle_message_evt(self, event_type, slack_event):
        """
        checks if a valid command is directed to bot,
        calls command handler for response, and posts response on slack
        """
        evt = slack_event['event']
        # if directed at bot, set text after the @ mention, whitespace removed
        print(evt.keys(), self.at_bot)
        if 'text' in evt.keys() and self.at_bot in evt['text']:
            text, channel = slack_event['text'], slack_event['channel']
            text = text.split(self.at_bot)[1].strip()
            pprint(text, channel)
            return
        else:  # if not text or message not directed at bot, skip
            return

        parsed = text.split(' ', 1)  # command and args (or None)
        # help command takes no arguments
        if len(parsed) == 1 and parsed[0] == 'help':
            response = self.handle_command('help')
        elif len(parsed) >= 2 and parsed[0] in self.commands:  # any command with at least one arg
            response = self.handle_command(parsed[0], parsed[1])
        else:  # invalid command
            response = self.default_response()

        # post result as attachment
        post_message = self.client.api_call("chat.postMessage",
                                            channel=channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text='response',
                                            attachments=response
                                            )
        print('message attachment posted!')

    def handle_command(self, command, args=None):
        """ finds each arg in appropriate APT dictionary
        and posts serialized result on Slack"""
        # as of now, help just returns default response
        if command == 'help':
            return self.serializer.default_attachment(self.commands)

        # other commands with no args could be added here later
        gids, groups= [], []
        for arg in args:
            gid = self.command_to_gid[command][arg]
            groups.append(self.gid_to_group[gid])

        return self.serializer.groups_attachment(groups)

    def default_response(self):
        return self.serializer.default_attachment(self.commands)








