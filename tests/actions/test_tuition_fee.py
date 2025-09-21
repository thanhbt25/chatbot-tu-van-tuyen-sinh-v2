import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from actions.actions_get_tuition_fee import ActionGetTuitionFee

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

action_get_fee = ActionGetTuitionFee()

slots1 = {
    "school": "dai oc bach khoa ha noi",
    "major": "khoa hoc may tinh",
    "year": "2025"
}
tracker1 = MockTracker(slots1, latest_message="None")
dispatcher1 = MockDispatcher()
action_get_fee.run(dispatcher1, tracker1, {})
print(dispatcher1.messages)