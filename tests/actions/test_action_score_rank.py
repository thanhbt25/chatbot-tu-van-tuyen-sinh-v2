import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from actions.actions_score_rank import ActionAskScoreRank
# Mocking Tracker và Dispatcher
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

# Khởi tạo action
action_ask_score_rank = ActionAskScoreRank()

# test case
slots1 = {"score": 25, "major": "cơ khí", "school": "bách khoa hà nội", "subject_combination": "A01", "quota": 300}
tracker1 = MockTracker(slots1)
dispatcher1 = MockDispatcher()
action_ask_score_rank.run(dispatcher1, tracker1, {})
print("\n--- Test Case 1 ---")
print(dispatcher1.messages[0])

slots2 = {"score": 29, "major": "công nghệ thông tin", "school": "đại học công nghệ - đại học quốc gia hà nội", "subject_combination": "A01", "quota": None}
tracker2 = MockTracker(slots2)
dispatcher2 = MockDispatcher()
action_ask_score_rank.run(dispatcher2, tracker2, {})
print("\n--- Test Case 2 ---")
print(dispatcher2.messages[0])
