import datetime
import os
import unittest

from telegram import Update, Message, Chat

FILENAME = 'tmp/test_image_original.png'


class TestImageHandler(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('tmp'):
            os.makedirs('tmp')

    def tearDown(self):
        if os.path.exists(FILENAME):
            os.remove(FILENAME)
