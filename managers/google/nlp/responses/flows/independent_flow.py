from typing import List, Optional
from dataclasses import dataclass
from managers.google.nlp.responses.responses import form_responses

def get_merged_responses(form_name: str, partner_id: str) -> dict:
    """Get merged responses for a given form and partner."""
    responses = form_responses.get("default", {}).get(form_name, {}).copy()
    
    partner_responses = form_responses.get(partner_id, {}).get(form_name, {})
    responses.update(partner_responses)
    
    return responses

@dataclass
class IndependentFSAID:
    state: str = "START"
    completed: bool = False

    def process_intent(self, intent: str, user_message: str = "", partner_id: Optional[str] = None) -> List[str]:
        if partner_id is None:
            raise ValueError("partner_id must be provided")

        if self.completed:
            self.reset_flow()
            return ["Flow Reset"]

        responses = get_merged_responses("independent_fsaid_form", partner_id)
        
        # State transitions
        transitions = {
            "START": self.handle_start,
            "Q1": self.handle_q1,
            "Q2": self.handle_q2,
            "Q3": self.handle_q3
        }

        handler = transitions.get(self.state)
        if handler:
            return handler(intent, responses)
        
        return ["I'm sorry, I didn't understand that. Can you please respond with 'yes' or 'no'?"]

    def handle_start(self, intent: str, responses: dict) -> List[str]:
        if intent == "independent":
            self.state = "Q1"
            return [responses.get('confirm_independent')]
        return []

    def handle_q1(self, intent: str, responses: dict) -> List[str]:
        if intent == "affirm":
            self.state = "Q2"
            return [responses.get('independent_personal_circumstances'), responses.get('independent_personal_circumstances_image')]
        elif intent == "deny":
            self.completed = True
            self.reset_flow()
            return [responses.get('independent_form_deny')]

    def handle_q2(self, intent: str, responses: dict) -> List[str]:
        if intent == "affirm":
            self.completed = True
            self.reset_flow()
            return [responses.get('independent_personal_circumstance'), responses.get('what_else_help')]
        elif intent == "deny":
            self.state = "Q3"
            return [responses.get('independent_unusual_circumstances'), responses.get('independent_unusual_circumstances_image')]

    def handle_q3(self, intent: str, responses: dict) -> List[str]:
        if intent == "affirm":
            self.completed = True
            self.reset_flow()
            return [responses.get('independent_unusual_circumstance'), responses.get('what_else_help')]
        elif intent == "deny":
            self.completed = True
            self.reset_flow()
            return [responses.get('independent_dependent'), responses.get('what_else_help')]

    def reset_flow(self):
        self.state = "START"
        self.completed = False