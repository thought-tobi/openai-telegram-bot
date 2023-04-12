import logging
import os
from typing import List, Tuple

import openai
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes

from src.session.session import get_user_session

FILTER_COLOUR = (255, 255, 255)
TOLERANCE = 5


async def handle_image_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    if not session.edit_image:
        # first image is the original image
        logging.info(f"Image editing session: received image from {update.effective_user.id}: "
                     f"{update.message.photo[-1].file_id} as original image")
        # download image
        img = await update.message.photo[-1].get_file()
        filename = f'tmp/{update.effective_user.id}_original.jpeg'
        await img.download_to_drive(filename)
        pre_process(filename)
        # update internal state
        session.start_image_edit_process()
        await update.message.reply_text("Send the modified image (draw a white shape over the area you want to edit), "
                                        "alongside a description of the edit you'd like to see.")
    else:
        # first image exists, this one is the modified one for editing
        logging.info(f"Image editing session: received image from {update.effective_user.id}: "
                     f"{update.message.photo[-1].file_id} as modified image")
        # download message
        img = await update.message.photo[-1].get_file()
        await img.download_to_drive(f'tmp/{update.effective_user.id}_modified.jpeg')
        pre_process(f'tmp/{update.effective_user.id}_modified.jpeg')
        await update.message.reply_text("Image received. Generating alternative...")

        # create alternative
        create_mask(f'{update.effective_user.id}')
        url = await create_alternative(original_file=f'tmp/{update.effective_user.id}_original.png',
                                       mask_file=f'tmp/{update.effective_user.id}_mask.png',
                                       prompt=update.message.caption)
        await update.message.reply_photo(photo=url)
        # cleanup
        session.stop_image_edit_process()
        os.remove(f'tmp/{update.effective_user.id}_original.png')
        os.remove(f'tmp/{update.effective_user.id}_modified.png')
        os.remove(f'tmp/{update.effective_user.id}_mask.png')


# generates mask from an image that contains a white area
def create_mask(filename: str) -> None:
    img = Image.open(f'tmp/{filename}_modified.png')
    # create empty pixel array
    pixels = [[(0, 0, 0, 255) for _ in range(img.height)] for _ in range(img.width)]
    # Iterate over each pixel in the image
    for x in range(img.width):
        for y in range(img.height):
            current_color = img.getpixel((x, y))
            # If the current pixel's color matches the transparent color,
            # set the alpha channel to 0 to make it transparent
            if pixel_approximates_filter_colour(current_color):
                pixels[x][y] = (255, 255, 255, 0)
    # save the image
    image_from_pixel_array(pixels).save(f'tmp/{filename}_mask.png')


def image_from_pixel_array(pixels: List[List[Tuple[int, int, int, int]]]) -> Image:
    img = Image.new('RGBA', (len(pixels), len(pixels[0])))
    for x in range(len(pixels)):
        for y in range(len(pixels[0])):
            img.putpixel((x, y), pixels[x][y])
    return img


def pixel_approximates_filter_colour(pixel: Tuple[int, int, int]) -> bool:
    r, g, b = pixel
    fr, fg, fb = FILTER_COLOUR
    # don't allow for a total deviation of more than 10 in any of the RGB values
    return abs((r - fr)) + abs((g - fg)) + abs((b - fb)) < TOLERANCE


async def create_alternative(original_file: str, mask_file: str, prompt: str) -> str:
    response = openai.Image.create_edit(
        image=open(original_file, "rb"),
        mask=open(mask_file, "rb"),
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url


def pre_process(filename: str) -> None:
    img = Image.open(filename)
    img.resize((1024, 1024)).save(filename
                                  .replace(".jpeg", "")
                                  .replace(".jpg", "") + ".png")
    os.remove(filename)


if __name__ == '__main__':
    img = Image.open("tmp/1965256751_modified.jpeg")
    img.resize((1024, 1024)).save("tmp/resize_test.png")
