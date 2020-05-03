#!/usr/bin/env python3

import keyboard
import queue
import time
import random
import threading


class Typist:
    def __init__(self, wpm, accuracy=100, error_deviation=0):
        self.characters = []
        self.characters_pointer = 0
        self.accuracy = accuracy
        self.error_deviation = error_deviation
        self.wpm = wpm
        self.cpm = self.wpm * 5
        keyboard.send(0)
        threading.Thread(target=self._type_loop).start()

    def _type_loop(self):
        while True:
            if len(self.characters) > self.characters_pointer:
                self._press_a_key(self.characters[self.characters_pointer])
                self.characters_pointer += 1
                self._make_a_mistake()
                if self.characters_pointer % 10 == 0:
                    change = random.randint(-5, 5)
                    if change == 0:
                        change = random.randint(-5, 5)
                    self.wpm += change
                    self.cpm = self.wpm * 5
            else:
                time.sleep(1)

    def _mistake_should_occur(self):
        if random.uniform(0, 100) > self.accuracy:
            return True
        return False

    def _write_a_few_more_letters(self, character_pointer):
        chance_to_write_another_letter = 80
        max_letters = len(self.characters) - character_pointer - 1
        counter = 0
        while max_letters > counter:
            if chance_to_write_another_letter > random.randint(1, 100):
                char = self.characters[character_pointer]
                if char == " ":
                    break
                self._press_a_key(char)
                character_pointer += 1
                chance_to_write_another_letter /= 2
                counter += 1
            else:
                break
        return counter

    def _get_mistake_type(self):
        mistakes_percent_chance = {1: 85, 2: 10, 3: 5}
        # mistakes_percent_chance = {1: 0, 2: 0, 3: 100}
        roll = random.randint(1, 100)
        comparator = 0
        for key in mistakes_percent_chance:
            comparator += mistakes_percent_chance[key]
            if roll <= comparator:
                return key

    def _get_neighbouring_letter(self, letter):
        rows = ["1234567890-=", "qwertyuiop[]", "asdfghjkl;'", "zxcvbnm,./"]
        letter = self._get_letter_in_good_form(letter)
        shifted = False
        if letter[0:6] == "shift+":
            letter = letter[6:]

        # find a neighbouring letter
        for row in rows:
            index = row.find(letter)
            if index == -1:
                continue
            elif index == 0:
                letter = row[1]
            elif index > 0 and index < len(row) - 1:
                side = random.randint(0, 1)
                if side:
                    letter = row[index + 1]
                letter = row[index - 1]
            elif index == len(row) - 1:
                letter = row[index - 1]

            if shifted:
                letter = "shift+" + letter
            return letter

    def _make_a_mistake(self):
        if self._mistake_should_occur():
            # mistake type 1: Switch letters and write a few more (also applies to spaces)
            # mistake type 2: Skip a letter and write a few more
            # mistake type 3: Keyboard mash
            mistake_type = self._get_mistake_type()
            if len(self.characters) - self.characters_pointer >= 2:
                if mistake_type == 1:
                    first_char = self.characters[self.characters_pointer]
                    second_char = self.characters[self.characters_pointer + 1]
                    if self._get_letter_in_good_form(first_char)[0:6] == "shift+":
                        return
                    if self._get_letter_in_good_form(second_char)[0:6] == "shift+":
                        return
                    if first_char == second_char:
                        return
                    self._press_a_key(second_char)
                    self._press_a_key(first_char)
                    letters_written = self._write_a_few_more_letters(self.characters_pointer + 2)
                    time.sleep(self._get_sleep_time() + 0.1)
                    for _ in range(letters_written + 2):
                        self._press_a_key("backspace")

                if mistake_type == 2:
                    second_char = self.characters[self.characters_pointer + 1]
                    self._press_a_key(second_char)
                    letters_written = self._write_a_few_more_letters(self.characters_pointer + 2)
                    time.sleep(self._get_sleep_time() + 0.1)
                    for _ in range(letters_written + 1):
                        self._press_a_key("backspace")

                if mistake_type == 3:
                    first_char = self.characters[self.characters_pointer]
                    additional_char = self._get_neighbouring_letter(first_char)
                    if additional_char is None:
                        return
                    self._press_a_key(first_char)
                    self._press_a_key(additional_char)
                    letters_written = self._write_a_few_more_letters(self.characters_pointer + 1)
                    time.sleep(self._get_sleep_time())
                    for _ in range(letters_written + 1):
                        self._press_a_key("backspace")
                    self.characters_pointer += 1

    def _get_letter_in_good_form(self, letter):
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

    def _press_a_key(self, letter, sleep_time=None):
        letter = self._get_letter_in_good_form(letter)

        if sleep_time is None:
            sleep_time = self._get_sleep_time()
        if letter[0:6] == "shift+":
            sleep_time *= 1.7
        time.sleep(sleep_time)

        keyboard.send(letter)

    def _get_sleep_time(self, char=None):
        roll = random.randint(0, 100) / 100
        sleep_duration = 60 / self.cpm
        sleep_duration += sleep_duration * (self.error_deviation * roll)
        return sleep_duration

    def insert_characters(self, string):
        self.characters += list(string)

    def _get_error_letter(self, char):
        if char.isalnum():
            if len(char) is 1:
                return "shift+" + char
            else:
                return char[-1]
        return char

    def stop_typing(self):
        self.characters = []

    def is_finished(self):
        if len(self.characters) - self.characters_pointer <= 1:
            return True
        return False


if __name__ == "__main__":
    time.sleep(1)
    typist = Typist(1500, 96.3, 1.5)

    for x in range(100):
        typist.insert_characters(
            """Size matters not. Look at me. Judge me by my size, do you? Hmm? Hmm. And well you should not. For my ally is the Force, and a powerful ally it is. Life creates it, makes it grow. Its energy surrounds us and binds us. Luminous beings are we, not this crude matter. You must feel the Force; around you; here, between you, me, the tree, the rock, everywhere, yes. Even between the land and the ship."""
        )