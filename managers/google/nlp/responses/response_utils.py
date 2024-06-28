from managers.google.nlp.responses.responses import qa_responses

def get_qa_response(intent: str, partner_id: str) -> dict:
    """Get QA response for a given intent and partner."""
    # Start with default responses
    default_responses = qa_responses.get("default", {})
    response = default_responses.get(intent, {}).copy()
    
    # Try to get the partner-specific response
    partner_responses = qa_responses.get(partner_id, {}).get(intent, {})
    response.update(partner_responses)
    
    return response