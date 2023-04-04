import datetime
from telegram import Message, Chat
from unittest import TestCase
from edit_message import EditMessage

chat = Chat(1, "some-type")


class TestEditMessage(TestCase):

    def test_should_replace_everything(self):
        # when
        message = Message(1, datetime.datetime.now(), chat, text="some-text")
        response = "some-other-text"
        edit_message = EditMessage(message)
        # then
        new_text = edit_message.replace(response)
        self.assertEqual("some-other-text", new_text)

    def test_should_replace_only_specific_word(self):
        # when
        message = Message(1, datetime.datetime.now(), chat, text="some-text")
        response = "another-reply"
        edit_message = EditMessage(message, 'text')
        # then
        new_text = edit_message.replace(response)
        self.assertEqual("some-another-reply", new_text)

    def test_should_work_with_special_characters(self):
        # when
        message = Message(1, datetime.datetime.now(), chat, text="some-text ...")
        response = "another-reply"
        edit_message = EditMessage(message, '...')
        # then
        new_text = edit_message.replace(response)
        self.assertEqual("some-text another-reply", new_text)