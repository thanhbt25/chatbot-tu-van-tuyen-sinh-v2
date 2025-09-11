from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from actions.utils.prediction import estimate_cutoff_multi

class ActionModelDetails(Action):
    def name(self) -> Text:
        return "action_model_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        school = tracker.get_slot("school")
        major = tracker.get_slot("major")
        score = tracker.get_slot("score")
        subject_combination = tracker.get_slot("subject_combination") or "A00"
        quota = tracker.get_slot("quota") or 100

        if not school or not major or not score:
            dispatcher.utter_message(text="Vui lòng cung cấp đầy đủ trường, ngành và điểm.")
            return []

        try:
            score = float(score)
        except ValueError:
            dispatcher.utter_message(text="Điểm nhập không hợp lệ.")
            return []

        msg = estimate_cutoff_multi(score, school, major, subject_combination, int(quota), return_details=True)

        dispatcher.utter_message(text=msg)
        return []
