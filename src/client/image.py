import logging
from typing import List

import openai


def create_image(prompt: str, number_images: int) -> List[str]:
    logging.info(f"Creating {number_images} original images.")
    openai_response = openai.Image.create(
        prompt=prompt,
        n=number_images,
        size="1024x1024"
    )
    return extract_image_urls_from_response(openai_response)


def create_alternative(image: str, number_images: int) -> List[str]:
    logging.info(f"Creating {number_images} image alternatives from image {image}.")
    openai_response = openai.Image.create_variation(
        image=image,
        n=number_images,
        size="1024x1024"
    )
    return extract_image_urls_from_response(openai_response)


async def create_edit(original_file: str, mask_file: str, prompt: str, number_images: int) -> List[str]:
    logging.info(f"Creating {number_images} image edits from files {original_file} and {mask_file}.")
    openai_response = openai.Image.create_edit(
        image=open(original_file, "rb"),
        mask=open(mask_file, "rb"),
        prompt=prompt,
        n=number_images,
        size="1024x1024"
    )
    return extract_image_urls_from_response(openai_response)


def extract_image_urls_from_response(response: str) -> List[str]:
    return [response["url"] for response in response["data"]]
