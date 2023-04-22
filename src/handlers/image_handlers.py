import logging
import os
from typing import List, Tuple

from PIL import Image
from telegram import Update

from src.client.image import create_edit, create_alternative
from src.session.session import get_user_session

FILTER_COLOUR = (255, 255, 255)
TOLERANCE = 5
START_EDIT_RESPONSE = "Send the modified image (draw a white shape over the area you want to edit), " \
                      "alongside a description of the edit you'd like to see."


async def _create_alternative(update: Update, count: int):
    await download_image(update, 'alternative')
    urls = create_alternative(f'tmp/{update.effective_user.id}_alternative.png', count)
    for url in urls:
        await update.message.reply_photo(photo=url)


async def handle_image_message(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)

    if update.message.caption == "/alternative":
        await _create_alternative(update, session.image_count)
        return

    image_status = 'original' if not session.edit_image else 'modified'
    await download_image(update, image_status)
    if not session.edit_image:
        session.start_image_edit_process()
        await update.message.reply_text(START_EDIT_RESPONSE)
    else:
        # create edit, todo update count argument
        await create_edit_images(update)
        await cleanup(session, update)


async def download_image(update: Update, image_status: str):
    logging.info(f"Image editing session: received image from {update.effective_user.id}: "
                 f"{update.message.photo[-1].file_id} as {image_status} image")
    img_id = await update.message.photo[-1].get_file()
    filename = f'tmp/{update.effective_user.id}_{image_status}.jpeg'
    await img_id.download_to_drive(filename)
    pre_process(filename)


async def create_edit_images(update: Update):
    await update.message.reply_text("Creating an edit ...")
    create_mask(f'{update.effective_user.id}')
    urls = await create_edit(original_file=f'tmp/{update.effective_user.id}_original.png',
                             mask_file=f'tmp/{update.effective_user.id}_mask.png',
                             prompt=update.message.caption,
                             number_images=get_user_session(update.effective_user.id).image_count)
    for url in urls:
        await update.message.reply_photo(photo=url)


async def cleanup(session, update):
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


def pre_process(filename: str) -> None:
    img = Image.open(filename)
    img.resize((1024, 1024)).save(filename
                                  .replace(".jpeg", "")
                                  .replace(".jpg", "") + ".png")
    os.remove(filename)
