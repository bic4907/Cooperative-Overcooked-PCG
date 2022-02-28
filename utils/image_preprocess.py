import numpy as np
import cv2
import copy

from PIL import ImageFont, ImageDraw, Image


def crop_and_resize(image: np.array) -> np.array:
    image = image[60:350, 45:483, :]
    image = cv2.resize(image, (200, 200))
    return image


def put_image(src: np.array, dest: np.array, x: int, y: int):
    width, height = src.shape[1], src.shape[0]

    assert y+height < dest.shape[0]
    assert x+width < dest.shape[1]

    new_image = copy.deepcopy(dest)
    new_image[y:y+height, x:x+width, :] = src / 255.

    return new_image


def put_text(src: np.array, text: str, size: int, x: int, y: int, rgba=(255, 255, 255, 0)):

    src = copy.deepcopy(src) * 255
    src = src.astype(np.uint8)

    font_path = "./fonts/NanumGothic-Regular.ttf"
    font = ImageFont.truetype(font_path, size)
    img_pil = Image.fromarray(src)
    draw = ImageDraw.Draw(img_pil)
    draw.text((x, y), text, font=font, fill=rgba)
    img = np.array(img_pil)

    img = img / 255.
    img = img.astype(np.float)

    return copy.deepcopy(img)
