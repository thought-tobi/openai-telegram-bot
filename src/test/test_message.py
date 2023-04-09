from unittest import TestCase
from src.data.message import Message


class TestMessage(TestCase):

    def test_should_count_words(self):
        assert Message(role="user", content="Hello World").calculate_tokens() == 2

    def test_should_count_words_with_punctuation(self):
        assert Message(role="user", content="Hello World!").calculate_tokens() == 3