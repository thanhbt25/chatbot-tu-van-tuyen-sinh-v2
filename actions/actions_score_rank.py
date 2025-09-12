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
        score = tracker.get_slot("score")
        subject_combination = tracker.get_slot("subject_combination")

        # Tính top %
        top_percent = score_percentage_rank(score, subject_combination)
        if top_percent > 0:       
            dispatcher.utter_message(
                text=f"Bạn đang ở top {round(top_percent*100, 2)}% cho tổ hợp {subject_combination}."
            )
        else:
            dispatcher.utter_message(
                text=f"Xin lỗi, trong cơ sở dữ liệu không tồn tại điểm như vậy. Liệu bạn có nhầm ở đâu không?"
            )

        return []
