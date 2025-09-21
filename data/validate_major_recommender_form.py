from rasa_sdk import FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
import re

class ValidateMajorRecommenderForm(FormValidationAction):
    def name(self) -> str:
        return "validate_major_recommender_form"

    async def validate_liked_subject(
        self,
        slot_value: str,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> dict:
        # Lấy câu người dùng gần nhất
        last_msg = tracker.latest_message.get("text", "").lower()
        
        liked = None
        disliked = None

        # Tìm các pattern "thích <môn>" và "không thích <môn>"
        liked_match = re.findall(r"(?:thích|mê|yêu) môn (\w+)", last_msg)
        disliked_match = re.findall(r"(?:không thích|ghét|không mê) môn (\w+)", last_msg)

        if liked_match:
            liked = ", ".join(liked_match)
        if disliked_match:
            disliked = ", ".join(disliked_match)

        # Nếu slot_value trùng với disliked_match thì gán slot_value vào disliked_subject
        if slot_value.lower() in disliked_match:
            disliked = slot_value
            liked = None
        elif slot_value.lower() in liked_match:
            liked = slot_value
            disliked = None
        # Trả về cả 2 slot
        return {"liked_subject": liked, "disliked_subject": disliked}
