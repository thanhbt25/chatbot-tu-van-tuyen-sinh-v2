from rasa_sdk import Action, Tracker 
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Union

from actions.utils.major_recommend import recommend_clusters
from services.gemini_response import paraphrase_response

def parse_subjects(subject_input: Union[str, List[str], None]) -> List[str]:
    if not subject_input:
        return []
    if isinstance(subject_input, list):
        return [s.strip() for s in subject_input if s and s.strip()]
    if isinstance(subject_input, str):
        subjects = [s.strip() for s in subject_input.replace(";", ",").split(",")]
        return [s for s in subjects if s]
    return []

class ActionMajorRecommender(Action):
    def name(self) -> Text:
        return "action_major_recommender"
    
    def run(
        self, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # ===== Lấy slot =====
        score_raw = tracker.get_slot("score")
        liked_subject_raw = tracker.get_slot("liked_subject")
        disliked_subject_raw = tracker.get_slot("disliked_subject")
        finance_requirement_raw = tracker.get_slot("finance_requirement")
        subject_combination = tracker.get_slot("subject_combination")

        print(f"debug: score={score_raw}, liked subjects={liked_subject_raw}, disliked subjects={disliked_subject_raw}, finance requirement raw = {finance_requirement_raw}, subject combination = {subject_combination}")

        # ===== Xử lý dữ liệu =====
        try:
            score = float(score_raw) if score_raw else None
        except ValueError:
            score = None

        try: 
            finance_requirement = float(finance_requirement_raw) if finance_requirement_raw else None
        except ValueError: 
            finance_requirement = None 

        liked_subjects = parse_subjects(liked_subject_raw)
        disliked_subjects = parse_subjects(disliked_subject_raw)

        if isinstance(subject_combination, str):
            subject_combination = [subject_combination]
        elif not subject_combination:
            subject_combination = []

        user_input = {
            "score": score, 
            "liked_subject": liked_subjects,
            "disliked_subject": disliked_subjects,
            "finance_requirement": finance_requirement,
            "subject_combination": subject_combination
        }

        # ===== Gọi recommend =====
        user_message = tracker.latest_message.get("text") 
        clusters = recommend_clusters(user_input, top_n=3)

        # ===== Tạo response =====
        response_texts = []
        for cluster in clusters:
            majors_list = ", ".join(cluster["sample_majors"])
            categories_list = ", ".join(cluster["major_category"].keys())
            response_texts.append(
                f"Ngành lớn: {categories_list}\n"
                f"Cluster đại diện: {cluster['representative_major']}\n"
                f"Ngành chi tiết: {majors_list}\n"
            )

        final_response = "\n---\n".join(response_texts)
        final_response = paraphrase_response(user_message, final_response)

        dispatcher.utter_message(text=final_response)
        return []
