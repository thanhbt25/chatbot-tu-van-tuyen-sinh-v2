from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.probability import score_percentage_rank
from services.gemini_response import paraphrase_response

class ActionAskScoreRank(Action):

    def name(self) -> Text:
        return "action_score_rank"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy slot
        score = tracker.get_slot("score")
        subject_combination = tracker.get_slot("subject_combination") or "A00"

        # Tính top %
        top_percent = score_percentage_rank(score, subject_combination)
        
        if top_percent > 0:       
            response = f"Bạn đang ở top {round(top_percent*100, 2)}% cho tổ hợp {subject_combination}."
        else:
            response = f"Xin lỗi, trong cơ sở dữ liệu không tồn tại điểm như vậy. Liệu bạn có nhầm ở đâu không?"

        user_messege = tracker.latest_message.get("text")
        improve_messege = paraphrase_response(user_messege, response)
        dispatcher.utter_message(text=improve_messege)
        return []
