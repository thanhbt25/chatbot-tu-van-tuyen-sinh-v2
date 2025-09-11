import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pandas as pd
from fuzzywuzzy import fuzz
from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher

# Import the functions and class from your original script
from actions.actions_benchmark import ActionBenchmark

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
# Create mock objects for the tracker and dispatcher
slots1 = {"school": "dai hoc cong nghe", "major": "cong nghe thong tin dinh huong nhat ban", "year": 2023}
tracker1 = MockTracker(slots1)
dispatcher1 = MockDispatcher()

# Create an instance of your action and run it 
action_benchmark = ActionBenchmark()
action_benchmark.run(dispatcher1, tracker1, {})

# Print the result to see the output 
print("--- Test case 1: All slots filled ---")
print(dispatcher1.messages[0])

# Test case 2: only school and major are filled (no year)
slots2 = {"school": "đại học kinh tế quốc dân", "major": "Kinh tế", "year": None}
tracker2 = MockTracker(slots2)
dispatcher2 = MockDispatcher()

action_benchmark.run(dispatcher2, tracker2, {})
print("\n--- Test case 2: School and major filled, no year ---")
print(dispatcher2.messages[0])

# Test case 3: missing school slot
slots3 = {"school": None, "major": "Kỹ thuật máy tính", "year": 2023}
tracker3 = MockTracker(slots3)
dispatcher3 = MockDispatcher()

action_benchmark.run(dispatcher3, tracker3, {})
print("\n--- Test Case 3: Missing school slot ---")
print(dispatcher3.messages[0])

# Test case 4: missing major slot
slots4 = {"school": "Đại học Bách khoa Hà Nội", "major": None, "year": 2023}
tracker4 = MockTracker(slots4)
dispatcher4 = MockDispatcher()

action_benchmark.run(dispatcher4, tracker4, {})
print("\n--- Test Case 4: Missing major slot ---")
print(dispatcher4.messages[0])

# Test Case 5: Misspelled name with missing accents
slots5 = {"school": "đai học bacskh hoa"}
tracker5 = MockTracker(slots5)
dispatcher5 = MockDispatcher()

action_benchmark.run(dispatcher5, tracker5, {})

print("\n--- Test Case 5: Misspelled name with missing accents ---")
print(dispatcher5.messages[0])

# Test Case 6: Missing key parts of the name (ambiguous)
slots6 = {"school": "quốc gia"}
tracker6 = MockTracker(slots6)
dispatcher6 = MockDispatcher()

action_benchmark.run(dispatcher6, tracker6, {})

print("\n--- Test Case 6: Ambiguous name, provide suggestions ---")
print(dispatcher6.messages[0])

