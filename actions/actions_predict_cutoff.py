from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from actions.utils.prediction import estimate_cutoff_multi
from actions.utils.help import extract_number
from services.gemini_response import paraphrase_response

class ActionPredictCutoff(Action):
    def name(self) -> Text:
        return "action_predict_cutoff"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        school = tracker.get_slot("school")
        major = tracker.get_slot("major")
        subject_combination = tracker.get_slot("subject_combination")
        quota = tracker.get_slot("quota")

        if isinstance(quota, str):
            quota = extract_number(quota)

        if quota == None: 
            cutoff = estimate_cutoff_multi(school, major, subject_combination)
        else: 
            cutoff = estimate_cutoff_multi(school, major, subject_combination, quota)

        response = ""

        if cutoff:
            response = f"Điểm chuẩn dự đoán cho ngành {major} tại {school} ≈ {round(cutoff,2)}"
        else:
            response = "Không đủ dữ liệu để dự đoán điểm chuẩn."

        user_messenge = tracker.latest_message.get("text")
        improve_response = paraphrase_response(user_messenge, response)
        dispatcher.utter_message(text=improve_response)

        return []
