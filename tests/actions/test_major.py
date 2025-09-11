import sys
import  os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')) )\

import pandas as pd
from fuzzywuzzy import fuzz
from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher

# Import the functions and class from your original script
from actions.actions_major import ActionMajor

# Make sure to replace 'your_script_name' (actions_benchmark) with the actual name of your file 

# Mocking the Rasa Tracker and Dispatcher for testing
class MockTracker:
    def __init__(self, slots):
        self._slots = slots

    def get_slot(self, key):
        return self._slots.get(key)
    
class MockDispatcher:
    def __init__(self):
        self.messages = []

    def utter_message(self, text=None, image=None, json_message=None):
        self.messages.append({"text": text, "image": image, "json": json_message})

# Test case 1: all slots are filled 
slots1 =  {"school": "đại học bách khoa hà nội"}
tracker1 = MockTracker(slots1)
dispatcher1 = MockDispatcher()

action_major = ActionMajor()
action_major.run(dispatcher1, tracker1, {})

print("--- Test case 1: All slots filled ---")
print(dispatcher1.messages[0])

# Test case 2: missing school slot
slots2 =  {"school": None}
tracker2 = MockTracker(slots2)
dispatcher2 = MockDispatcher()
action_major.run(dispatcher2, tracker2, {})

print("\n--- Test case 2: Missing school slot ---")
print(dispatcher2.messages[0])

# Test case 3: Tên trường không chuẩn và không có trong dữ liệu
slots3 = {"school": "dai hoc hai duong"}
tracker3 = MockTracker(slots3)
dispatcher3 = MockDispatcher()

action_major = ActionMajor()
action_major.run(dispatcher3, tracker3, {})

print("\n--- Test case 3: Tên trường không chuẩn và không có trong dữ liệu ---")
print(dispatcher3.messages[0])

# Test case 4: Tên trường không chuẩn nhưng có trong dữ liệu
slots4 = {"school": "bach khoa hcm"}
tracker4 = MockTracker(slots4)
dispatcher4 = MockDispatcher()

action_major = ActionMajor()
action_major.run(dispatcher4, tracker4, {})

print("\n--- Test case 4: Tên trường không chuẩn nhưng có trong dữ liệu ---")
print(dispatcher4.messages[0])

# Test case 5: Tên trường gõ sai, cần gợi ý
slots5 = {"school": "đai học công nghệ thông tin"}
tracker5 = MockTracker(slots5)
dispatcher5 = MockDispatcher()

action_major = ActionMajor()
action_major.run(dispatcher5, tracker5, {})

print("\n--- Test case 5: Tên trường gõ sai, cần gợi ý ---")
print(dispatcher5.messages[0])
