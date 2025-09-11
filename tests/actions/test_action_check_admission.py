import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from actions.actions_admission_chance import ActionCheckAdmissionChance

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
action_admission = ActionCheckAdmissionChance()

# ==== TEST CASES ====

# Case 1: đầy đủ score, major, school
slots1 = {"score": 25, "major": "cơ khí", "school": "bách khoa hà nội", "subject_combination": "A01", "quota": None}
tracker1 = MockTracker(slots1)
dispatcher1 = MockDispatcher()
action_admission.run(dispatcher1, tracker1, {})
print("\n--- Test Case 1: Full slots (score, major, school) ---")
print(dispatcher1.messages[0])

# Case 2: có score + school, không có major
slots2 = {"score": 20.5, "major": None, "school": "đại học fpt", "subject_combination": "B01", "quota": None}
tracker2 = MockTracker(slots2)
dispatcher2 = MockDispatcher()
action_admission.run(dispatcher2, tracker2, {})
print("\n--- Test Case 2: Missing major ---")
print(dispatcher2.messages[0])

# Case 3: score + school + major + subject_combination
slots3 = {"score": 27.5, "major": None, "school": "đại học y hà nội", "subject_combination": "A00", "quota": None}
tracker3 = MockTracker(slots3)
dispatcher3 = MockDispatcher()
action_admission.run(dispatcher3, tracker3, {})
print("\n--- Test Case 3: With subject_combination ---")
print(dispatcher3.messages[0])

# Case 4: score + subject_combination + school + major
slots4 = {"score": 21, "major": "kinh tế quốc tế", "school": "đại học kinh tế quốc dân", "subject_combination": "A01", "quota": None}
tracker4 = MockTracker(slots4)
dispatcher4 = MockDispatcher()
action_admission.run(dispatcher4, tracker4, {})
print("\n--- Test Case 4: Full with subject_combination ---")
print(dispatcher4.messages[0])

# Case 5: score + quota + school + major
slots5 = {"score": 27.75, "major": "y khoa", "school": "trường đại học y dược - đại học quốc gia hà nội", "subject_combination": "B00", "quota": 100}
tracker5 = MockTracker(slots5)
dispatcher5 = MockDispatcher()
action_admission.run(dispatcher5, tracker5, {})
print("\n--- Test Case 5: With quota ---")
print(dispatcher5.messages[0])

# Case 6: quota + score + subject_combination
slots6 = {"score": 28.00, "major": "khoa học máy tính", "school": "trường đại học bách khoa hà nội", "subject_combination": "A00", "quota": 200}
tracker6 = MockTracker(slots6)
dispatcher6 = MockDispatcher()
action_admission.run(dispatcher6, tracker6, {})
print("\n--- Test Case 6: With subject_combination and quota ---")
print(dispatcher6.messages[0])

# Case 7: chỉ có score + major
slots7 = {"score": 16, "major": "marketing", "school": None, "subject_combination": None, "quota": None}
tracker7 = MockTracker(slots7)
dispatcher7 = MockDispatcher()
action_admission.run(dispatcher7, tracker7, {})
print("\n--- Test Case 7: Only score and major ---")
print(dispatcher7.messages[0])

# Case 8: quota nhỏ, ngành kỹ thuật vật liệu
slots8 = {"score": 23, "major": "kĩ thuật vật liệu", "school": None, "subject_combination": None, "quota": 20}
tracker8 = MockTracker(slots8)
dispatcher8 = MockDispatcher()
action_admission.run(dispatcher8, tracker8, {})
print("\n--- Test Case 8: With quota (kĩ thuật vật liệu, quota=20) ---")
print(dispatcher8.messages[0])

# Case 9: quota trung bình, ngành giáo dục tiểu học
slots9 = {"score": 19.5, "major": "giáo dục tiểu học", "school": "đại học sư phạm hà nội", "subject_combination": "B00", "quota": 50}
tracker9 = MockTracker(slots9)
dispatcher9 = MockDispatcher()
action_admission.run(dispatcher9, tracker9, {})
print("\n--- Test Case 9: With quota (giáo dục tiểu học, quota=50) ---")
print(dispatcher9.messages[0])

# Case 10: quota lớn, ngành khoa học máy tính
slots10 = {"score": 25, "major": "khoa học máy tính", "school": "đại học bách khoa hà nội", "subject_combination": "A06", "quota": 300}
tracker10 = MockTracker(slots10)
dispatcher10 = MockDispatcher()
action_admission.run(dispatcher10, tracker10, {})
print("\n--- Test Case 10: With quota (CNTT, quota=300) ---")
print(dispatcher10.messages[0])

# Case 11: quota 150, ngành y đa khoa
slots11 = {"score": 24, "major": "y đa khoa", "school": "đại học y hà nội", "subject_combination": "C02", "quota": 150}
tracker11 = MockTracker(slots11)
dispatcher11 = MockDispatcher()
action_admission.run(dispatcher11, tracker11, {})
print("\n--- Test Case 11: With quota (y đa khoa, quota=150) ---")
print(dispatcher11.messages[0])

# Case 12: quota 80, ngành công nghệ thông tin
slots12 = {"score": 22, "major": "công nghệ thông tin", "school": "trường đại học hàng hải việt nam", "subject_combination": "A01", "quota": 80}
tracker12 = MockTracker(slots12)
dispatcher12 = MockDispatcher()
action_admission.run(dispatcher12, tracker12, {})
print("\n--- Test Case 12: With quota (CNTT, quota=80) ---")
print(dispatcher12.messages[0])
