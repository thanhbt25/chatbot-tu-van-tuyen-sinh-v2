from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from actions.utils.prediction import predict_cutoff
from actions.utils.data_loader import benchmark_df

class ActionPredictCutoff(Action):
    def name(self) -> Text:
        return "action_predict_cutoff"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        school = tracker.get_slot("school")
        major = tracker.get_slot("major")

        if not school or not major:
            dispatcher.utter_message(text="Bạn cần cung cấp tên trường và ngành.")
            return []

        cutoff = predict_cutoff(school, major)
        if cutoff:
            dispatcher.utter_message(text=f"Điểm chuẩn dự đoán cho ngành {major} tại {school} ≈ {round(cutoff,2)}")
        else:
            dispatcher.utter_message(text="Không đủ dữ liệu để dự đoán điểm chuẩn.")

        return []
