#!/usr/bin/env python3
from PIL import Image
import pytesseract
import autocorrect
import time
import pyscreenshot
import cv2
import numpy as np
import keyboard
from typist import Typist
from datetime import datetime
import mouse
import config

def get_lines(img):
    """
    This function creates a mask containing the two strikethrough lines
    in the captcha image
    """
    thresh = 60
    fn = lambda x: 255 if x > thresh else 0
    img = img.convert("L").point(fn, mode="1")
    # img.show()
    return img


def process_typeracer_captcha(img):
    mask = get_lines(img)
    white = Image.new("RGBA", img.size, (255, 255, 255))
    img = Image.composite(img, white, mask)
    thresh = 150
    fn = lambda x: 255 if x > thresh else 0
    img = img.convert("L").point(fn, mode="1")
    # img.show()
    return img


def image_ocr_captcha(img_path):
    """
    Performs OCR on an image and returns the text as a string
    """
    img = Image.open(str(img_path))
    img = process_typeracer_captcha(img)
    text = pytesseract.image_to_string(
        img,
        config='-c tessedit_char_whitelist=" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz,."',
    ).replace("\n", " ")
    return text


def image_ocr_race(img):
    text = pytesseract.image_to_string(
        # img, config='-c tessedit_char_blacklist=“|’‘"§\\”'
        img, config='-c tessedit_char_blacklist="“|’‘|’‘§\\”"'
    ).replace("\n", " ")
    return text


def autocorrect_words(text):
    speller = autocorrect.Speller(lang="en")
    words = text.split(" ")
    for i in range(len(words)):
        try:
            corrected_word = speller(words[i])
            # print(word[i], "=", corrected_word)
            word[i] = corrected_word
        except:
            pass
    text = " ".join(words)
    return text


def get_race_textbox():
    bbox = (config.box_width_left, 250, config.box_width_right, 768)
    img = pyscreenshot.grab(bbox=bbox, backend="pygdk3")
    img.save("/tmp/textbox_containing_image.png")
    img_rgb = cv2.imread("/tmp/textbox_containing_image.png")
    dotted_line = cv2.imread(config.dotted_line)
    change_dispay_format_text = cv2.imread(config.change_display_format)

    # search for the dotted line graphic and save the height of the lowest one
    res = cv2.matchTemplate(img_rgb, dotted_line, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    search_height = 0
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        search_height = pt[1]
    

    top_left = (config.box_width_left, search_height + 20 + bbox[1])

    res = cv2.matchTemplate(img_rgb, change_dispay_format_text, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    search_height = 1000
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        search_height = pt[1]

    bottom_right = (config.box_width_right, search_height + 5 + bbox[1])
    bounding_box = (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
    img = pyscreenshot.grab(bbox=bounding_box, backend="pygdk3")
    # thresh = 160
    # fn = lambda x: 255 if x > thresh else 0
    # img = img.convert("L").point(fn, mode="1")
    img.quantize(2)
    return img, bounding_box

def check_for_yellow_light():
    bbox_dimensions = config.yellow_light_position
    img = pyscreenshot.grab(bbox=bbox_dimensions, backend='pygdk3')
    img.save("/tmp/yellow_light_full_screen.png")
    found_a_yellow_light = False
    img_rgb = cv2.imread('/tmp/yellow_light_full_screen.png')
    yellow_light = cv2.imread(config.yellow_light)
    res = cv2.matchTemplate(img_rgb, yellow_light, cv2.TM_CCOEFF_NORMED)
    threshold = .9
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        found_a_yellow_light = True

    return found_a_yellow_light

def wait_for_text_to_be_written(seconds, poll_coords):
    """
    Waits for the text to be written and checks if there are typos during writing
    """
    starting_time = time.time()
    typos_counter = 0
    while time.time() < starting_time + seconds:
        # check if a typo has occured
        box = (poll_coords[0], poll_coords[1], poll_coords[0] + 1, poll_coords[1] + 1)
        img = pyscreenshot.grab(bbox=box, backend='pygdk3')
        if img.getpixel((0,0)) != (250, 250, 250):
            if typos_counter >= 12:
                return True
            mouse.move(poll_coords[0], poll_coords[1])
            typos_counter += 1
        else:
            typos_counter = 0
        if typos_counter == 0:
            time.sleep(0.25)

    return False # no typo

def open_website(link):
    wpm = 250
    keyboard.send("f6")
    time.sleep(0.1)
    typist = Typist(wpm)
    typist.insert_characters(link)
    sleep_time = (len(link) / (wpm * 5)) * 60 + 1.5
    time.sleep(sleep_time)
    keyboard.send("enter")

def enter_race():
    # enter a race
    keyboard.send("ctrl+alt+i")
    mouse.move(200, 600)

def search_for_yellow_light():
    max_attempts = 60
    for _ in range(max_attempts):
        if check_for_yellow_light():
            return True
    return False

def get_typing_content():
    img, bounding_box = get_race_textbox()
    text = image_ocr_race(img).replace("ﬁ", "I").replace("ﬂ", "I").replace("M/", "W").replace(" [ ", " I ").replace(" ] ", " I ").replace(" 1 ", " I ").replace(" ! ", " I ")
    if len(text) != 0:
        if text[0] == "1" or text[0] == "i" or text[0] == "l":
            text = "I" + text[1:]
    return text, bounding_box

def find_text_continuation(premature_text, text, index):
    if len(premature_text) < index:
        index = len(premature_text)
    word_length = 5
    sought_chunk = premature_text[index:index + word_length]
    for x in range(-3, 4):
        # find the common point between the texts
        if text[x + index: x + index + word_length] == sought_chunk:
            return text[x + index:]
    return text # couldn't merge - fallback behaviour


def race_bot():
    # wait for the user to open the typeracer website
    time.sleep(3)

    successful_types = 0
    unsuccessful_types = 0

    while True:
        open_website("https://typeracer.com/")
        time.sleep(5) # wait for it to load

        enter_race()

        if not search_for_yellow_light():
            continue
        # premature quote grab
        premature_text, _ = get_typing_content()
        typist = Typist(config.wpm, config.accuracy, config.error_deviation)
        time.sleep(3.4)
        typist.insert_characters(premature_text[0:25])
        time.sleep(0.5)
        # take a screenshot and save it
        text, bounding_box = get_typing_content()
        text_continuation = find_text_continuation(premature_text, text, 25)
        typist.insert_characters(text_continuation)
        text = premature_text[0:25] + text_continuation
        textbox_location = (config.mouse_width_typebox, bounding_box[3] + config.mouse_offset_of_change_display_typebox)
        while not typist.is_finished():
            typo_flag = wait_for_text_to_be_written(3, textbox_location)
            if typist.is_finished():
                typo_flag = False
                break
            if typo_flag:
                break
        typist.stop_typing()

        if typo_flag:
            append = "typo"
            unsuccessful_types += 1
        else:
            append = "correct"
            successful_types += 1

        with open("quotes_log_" + append + ".txt", 'a') as f:
            f.write(text + "\n")

        time.sleep(0.3)
        print("Sucessful: {} | Unsuccessful: {}".format(successful_types, unsuccessful_types))
        

if __name__ == "__main__":
    keyboard.send(0)
    mouse.wait(target_types=(mouse.DOWN))
    # print(mouse.get_position())
    race_bot()