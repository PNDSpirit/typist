#!/usr/bin/env python3

import keyboard
import queue
import time
import random
import threading


class Typist:
    def __init__(self):
        self.characters_queue = queue.SimpleQueue()
        self.accuracy = 100
        self.error_deviation = 0.2
        self.wpm = 165
        self.cpm = self.wpm * 5
        self.characters_written = 0
        keyboard.send(0)
        threading.Thread(target=self._type_loop).start()

    def _type_loop(self):
        while True:
            try:
                char = self.characters_queue.get(timeout=5)
            except queue.Empty:
                print("Queue is empty")
                return
            if char is not None:
                self._press_a_key(char)

            self._make_a_mistake()

    def _make_a_mistake(self):
        pool_size = 10000
        chance = (100 - self.accuracy) / 100
        roll = random.randint(0, pool_size - 1)

        if roll < pool_size * chance:
            # write and delete a char
            self._press_a_key("0")
            self._press_a_key("backspace")

    def _press_a_key(self, letter):
        if len(letter) is 1 and letter.isupper():
            letter = "shift+" + letter.lower()
        keyboard.send(letter)
        time.sleep(self._get_sleep_time())
        print("working")

    def _get_sleep_time(self, char=None):
        roll = random.randint(-100, 100) / 100
        sleep_duration = 60 / self.cpm
        sleep_duration += sleep_duration * (self.error_deviation * roll)
        return sleep_duration

    def insert_characters(self, chars):
        for char in chars:
            self.characters_queue.put(char)


if __name__ == "__main__":
    # time.sleep(5)
    typist = Typist()
    typist.insert_characters("hi")
    typist.insert_characters("hi")
