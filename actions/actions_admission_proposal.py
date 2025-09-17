from rasa_sdk import Action, Tracker 
from rasa_sdk.executor import CollectingDispatcher
from services.gemini_response import get_admission_proposal
from typing import Any, Text, Dict, List

class ActionMajorInfo(Action):
    def name(self) -> Text:
        return "action_admission_proposal"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        school = tracker.get_slot("school")

        user_messenge = tracker.latest_message.get("text")
        response = get_admission_proposal(school, user_messenge)
        dispatcher.utter_message(text=response)
