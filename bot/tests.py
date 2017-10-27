import unittest
from bot import Bot

class TestAptBot(unittest.TestCase):
    def __init__(self):
        self.bot = Bot()

    def test_help(self):
        length = self.bot.handle_command('help')
        self.assertEqual(length, 0)

    def test_invalid(self):
        length = self.bot.handle_command('group')
        self.assertEqual(length, 0)

    def test_group(self):
        length = self.bot.handle_command('group APT 2')
        self.assertEqual(length, 4)

    def test_tool(self):
        length = self.bot.handle_command('tool backdoor')
        self.assertEqual(length, 8)

    def test_target(self):
        length = self.bot.handle_command('target japan')
        self.assertEqual(length, 4)

    def test_ops(self):
        length = self.bot.handle_command('ops desert')
        self.assertEqual(length, 1)

if __name__ == '__main__':
    unittest.main()
