from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.probability import score_percentage_rank

class ActionAskScoreRank(Action):

    def name(self) -> Text:
        return "action_score_rank"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy slot
        user_score = tracker.get_slot("score")
        subject_combination = tracker.get_slot("subject_combination")

        # Nếu chưa có slot thì hỏi
        if not user_score:
            dispatcher.utter_message(text="Bạn được bao nhiêu điểm?")
            return []
        if not subject_combination:
            dispatcher.utter_message(text="Bạn muốn tính top % cho tổ hợp môn nào?")
            return []

        # Tính top %
        top_percent = score_percentage_rank(user_score, subject_combination)
        dispatcher.utter_message(
            text=f"Bạn đang ở top {round(top_percent*100, 2)}% cho tổ hợp {subject_combination}."
        )

        return []
