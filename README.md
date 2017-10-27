# AptBot

### What is AptBot?
AptBot is a Slack bot for retrieving data about Advanced Persistent Threat (APT) groups.

An advanced persistent threat (APT) is a network attack in which an unauthorized person gains access to a network and stays there undetected for a long period of time.

### Using AptBot

AptBot provides the following four commands:

group - information about the APT group(s) containing the given name

tool - list of APT groups that use the given tool

target - list of APT groups that target the given asset or organization

ops - list of APT group that executed the given operation

### Installing AptBot
Since AptBot is currently not distributed on Slack, the bot must be added manually to your team.

Please do the following:

0) install the dependencies in requirments.txt and create virtual environment

1) go to https://chatbot-example-1.slack.com/apps/new/A0F7YS25R-bots

2) set bot username to be 'aptbot' and press add bot integration. This redirects to a page showing your API Token.

3) export the API Token using: export BOT_TOKEN='<your API token>'

4) run using: python bot.py

5) open your team's slack and begin asking AptBot about Advanced Persistent Attacks by typing: @aptbot help

### ToDo
use SQL to simplify queries

refactor to an app and distribute

### References
Following sources were used while building the bot:

https://github.com/hslatman/awesome-threat-intelligence

https://docs.google.com/spreadsheets/u/1/d/1H9_xaxQHpWaa4O_Son4Gx0YOIzlcBWMsdvePFX68EKU/pubhtml

https://www.fullstackpython.com/blog/build-first-slack-bot-python.html


