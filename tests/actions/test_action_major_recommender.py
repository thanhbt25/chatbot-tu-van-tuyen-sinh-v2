import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from actions.actions_recommend_major import ActionMajorRecommender


# Mocking Tracker và Dispatcher
class MockTracker:
    def __init__(self, slots, latest_message=""):
        self._slots = slots
        self.latest_message = {"text": latest_message}  # giả lập giống Rasa

    def get_slot(self, key):
        return self._slots.get(key)


class MockDispatcher:
    def __init__(self):
        self.messages = []

    def utter_message(self, text=None, image=None, json_message=None):
        self.messages.append({"text": text, "image": image, "json": json_message})


# Khởi tạo action
action_major_recommender = ActionMajorRecommender()

# Testcase 1
slots1 = {
    "score": 29.0,
    "liked_subject": "toán, anh",
    "disliked_subject": "hóa",
    "finance_requirement": 30000000,
    "subject_combination": "A01"
}
tracker1 = MockTracker(
    slots1,
    latest_message="Tôi được 29.0 điểm khối A01 nhưng mà tôi thích toán, anh"
                   "và không thích hóa lắm, số tiền tôi có thể trả là 30 triệu."
)
dispatcher1 = MockDispatcher()

# Gọi action
action_major_recommender.run(dispatcher1, tracker1, {})

print("\n-- TESTCASE 1 --")
print(dispatcher1.messages[0])
