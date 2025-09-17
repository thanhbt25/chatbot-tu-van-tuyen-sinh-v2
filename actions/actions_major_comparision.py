from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Union

from services.gemini_response import get_major_comparision_answer

class ActionMajorComparision(Action):
    def name(self) -> Text:
        return "action_major_comparision"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text")
        response = get_major_comparision_answer(user_messenge=user_message)
        dispatcher.utter_message(text=response)
        return []
