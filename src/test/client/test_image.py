from unittest import TestCase
from unittest.mock import MagicMock

import openai

MOCK_RESPONSE = {
    "created": 1681456145,
    "data": [
        {
            "url": "some-url"
        }
    ]
}


class TestImage(TestCase):

    def test_should_create_exactly_one_image(self):
        # when
        openai.Image.create = MagicMock(return_value=MOCK_RESPONSE)
        prompt = "prompt"
        number_images = 1
        response = create_image(prompt, number_images)

        # then
        openai.Image.create.assert_called_once_with(
            prompt=prompt,
            n=number_images,
            size="1024x1024"
        )

        self.assertEqual(["some-url"], response)

    def test_should_create_multiple_images(self):
        # when
        MOCK_RESPONSE["data"].append({"url": "some-other-url"})
        openai.Image.create = MagicMock(return_value=MOCK_RESPONSE)
        prompt = "prompt"
        number_images = 2
        response = create_image(prompt, number_images)

        # then
        openai.Image.create.assert_called_once_with(
            prompt=prompt,
            n=number_images,
            size="1024x1024"
        )

        self.assertEqual(["some-url", "some-other-url"], response)
