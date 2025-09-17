from rasa_sdk import Action, Tracker 
from rasa_sdk.executor import CollectingDispatcher
from services.gemini_response import major_info_answer
from typing import Any, Text, Dict, List

class ActionMajorInfo(Action):
    def name(self) -> Text:
        return "action_major_info"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("major")

        user_messenge = tracker.latest_message.get("text")
        response = major_info_answer(major, user_messenge)
        dispatcher.utter_message(text=response)
