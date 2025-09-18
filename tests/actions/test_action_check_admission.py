import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from actions.actions_admission_probability import ActionAdmissionProbability

# Mock Tracker và Dispatcher
class MockTracker:
    def __init__(self, slots, latest_message=""):
        self._slots = slots
        self.latest_message = {"text": latest_message}

    def get_slot(self, key):
        return self._slots.get(key)

class MockDispatcher:
    def __init__(self):
        self.messages = []

    def utter_message(self, text=None, image=None, json_message=None):
        self.messages.append({"text": text, "image": image, "json": json_message})

# Khởi tạo action
action_admission_probability = ActionAdmissionProbability()

# Test case 1
slots1 = {
    "score": "25", 
    "major": "cong nghe thong tin", 
    "school": "dai hoc cong nghe - dai hoc quoc gia ha noi", 
    "year": "2025"
}
tracker1 = MockTracker(slots1, latest_message="Mình có 25 điểm CNTT ở ĐH Công Nghệ")
dispatcher1 = MockDispatcher()
action_admission_probability.run(dispatcher1, tracker1, {})
print("\n--- Test Case 1 ---")
print(dispatcher1.messages)

# Test case 2
slots2 = {
    "score": "29", 
    "major": "khoa hoc may tinh", 
    "school": "dai hoc bach khoa ha noi", 
    "year": "2026"
}
tracker2 = MockTracker(slots2, latest_message="29 điểm KHMT Bách Khoa HN")
dispatcher2 = MockDispatcher()
action_admission_probability.run(dispatcher2, tracker2, {})
print("\n--- Test Case 2 ---")
print(dispatcher2.messages)
