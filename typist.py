#!/usr/bin/env python3

import keyboard
import queue
import time
import random
import threading


class Typist:
    def __init__(self, wpm, accuracy=100, error_deviation=0):
        self.characters_queue = queue.SimpleQueue()
        self.accuracy = accuracy
        self.error_deviation = error_deviation
        self.wpm = wpm
        self.cpm = self.wpm * 5

        keyboard.send(0)
        threading.Thread(target=self._type_loop).start()

    def _type_loop(self):
        while True:
            try:
                char = self.characters_queue.get(timeout=5)
            except queue.Empty:
                return

            if char is not None:
                self._press_a_key(char)
                self._make_a_mistake(char)

    def _make_a_mistake(self, char):
        pool_size = 10000
        chance = (100 - self.accuracy) / 100
        roll = random.randint(0, pool_size - 1)

        if roll < pool_size * chance:
            # write and delete a char
            self._press_a_key(char)
            self._press_a_key("backspace")

    def get_letter_in_good_form(self, letter):
        shifted_keys = {
            "!": "1",
            "@": "2",
            "#": "3",
            "$": "4",
            "%": "5",
            "^": "6",
            "&": "7",
            "*": "8",
            "(": "9",
            ")": "0",
            ":": ";",
            '"': "'",
            "{": "[",
            "}": "]",
            "+": "=",
            "_": "-",
            "<": ",",
            ">": ".",
            "?": "/",
            "~": "`",
        }

        if len(letter) is 1:
            if letter.isupper():
                letter = "shift+" + letter.lower()
            if letter in shifted_keys.keys():
                letter = "shift+" + shifted_keys[letter]

        return letter

    def _press_a_key(self, letter):
        letter = self.get_letter_in_good_form(letter)
        keyboard.send(letter)
        time.sleep(self._get_sleep_time())

    def _get_sleep_time(self, char=None):
        roll = random.randint(-100, 100) / 100
        sleep_duration = 60 / self.cpm
        sleep_duration += sleep_duration * (self.error_deviation * roll)
        return sleep_duration

    def insert_characters(self, chars):
        for char in chars:
            self.characters_queue.put(char)

    def _get_error_letter(self, char):
        if char.isalnum():
            if len(char) is 1:
                return "shift+" + char
            else:
                return char[-1]
        return char

    def stop_typing(self):
        self.characters_queue = queue.SimpleQueue()


if __name__ == "__main__":
    time.sleep(1)
    typist = Typist()
    typist.insert_characters("""We just don't recognize life's most significant moments while they're happening. Back then I thought, "Well, there'll be other days." I didn't realize that was the only day.""")
