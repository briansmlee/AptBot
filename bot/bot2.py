# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os
import message

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "aptbot"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        # self.messages = {}

        self.serializer = Serializer()
        self.AT_BOT = "<@" + BOT_ID ">"
        self.commands = {
            'group': 'information about the APT group(s) containing the given name',
            'tool': 'list of APT groups that use the given tool',
            'target': 'list of APT groups that target the given asset or organization',
            'ops': 'list of APT group that executed the given operation'
        }

        path = '../data/APT_dict.pkl'
        with open(self.pkl_path, 'rb') as f:
            self.gid_to_group = pickle.load(f)  # dict of groups
        with open(self.path + '', 'rb') as f:
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
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def handle_message_evt(self, event_type, slack_event):
        """ checks if a valid command is directed to bot and calls command handler """

        # if directed at bot, set text after the @ mention, whitespace removed
        if 'text' in slack_event.keys() and self.at_bot in slack_event['text']:
            text, channel = slack_event['text'], slack_event['channel']
            text = text.split(self.at_bot)[1].strip()
        else:  # if not text or message not directed at bot, skip
            return

        parsed = text.split(' ', 1)  # command and args (or None)
        # help command takes no arguments
        if len(parsed) == 1 and parsed[0] == 'help':
            response = self.handle_command(channel, 'help')
        elif len(parsed) >= 2 and parsed[0] in self.commands:  # any command with at least one arg
            response = self.handle_command(channel, parsed[0], parsed[1])
        else:  # invalid command
            response = self.default_response()


    def handle_command(self, channel, command, args=None):
        """ finds each arg in appropriate APT dictionary
        and posts serialized result on Slack"""
        if command == 'help':
            return self.serializer.default_attachment(self.commands)

        # other commands with no args could be added later
        gids, groups= [], []
        for arg in args:
            gid = self.command_to_gid[command][arg]
            groups.append(self.gid_to_group[gid])

        return self.serializer.groups_attachment(groups)

    def default_response(self):
        return self.serializer.default_attachment(self.commands)








