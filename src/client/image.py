from typing import List

import openai


def create_image(prompt: str, number_images: int) -> List[str]:
    openai_response = openai.Image.create(
        prompt=prompt,
        n=number_images,
        size="1024x1024"
    )
    return extract_image_urls_from_response(openai_response)


def extract_image_urls_from_response(response: str) -> List[str]:
    return [response["url"] for response in response["data"]]