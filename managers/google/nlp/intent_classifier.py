
import os
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from managers.google.sms_handler import SMSHandler
from managers.google.nlp.responses.flows.fafsa_eligibility_flow import FAFSAEligibilityFlow
from managers.google.nlp.responses.flows.student_fsaid_flow import StudentFafsa
from managers.google.nlp.responses.flows.which_parent_fsaid_flow import WhichParentFSAID
from managers.google.nlp.responses.flows.independent_flow import IndependentFSAID
from managers.google.nlp.responses.flows.which_parent_invite_flow import WhichParentInvite
from managers.google.nlp.responses.flows.parent_fsaid_flow import ParentFafsa
from managers.google.nlp.nn_trainer import IntentClassifierModel
from managers.google.nlp.data.intents import intent_data
from managers.google.nlp.responses.response_utils import get_qa_response
from dotenv import load_dotenv
import logging

load_dotenv()

FAFSA_SERVER_URL = os.getenv("BASE_URL")
LOAD_MODEL_PATH = os.getenv("LOAD_MODEL_PATH")

class IntentClassifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), LOAD_MODEL_PATH)

        # Prepare data and dynamically determine input and output dimensions
        self.vectorizer = TfidfVectorizer()
        texts = self._get_training_texts()
        X_tfidf = self.vectorizer.fit_transform(texts).toarray()
        input_dim = X_tfidf.shape[1]
        output_dim = len(intent_data)

        logging.info("Vectorizer initialized and fitted with training texts.")

        # Initialize the model architecture
        self.model = IntentClassifierModel(input_dim, output_dim)

        # Load the state dictionary
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()  # Set the model to evaluation mode
        logging.info(f"Model loaded from {model_path}")

        # Create a mapping from indices to intents
        self.index_to_intent = {index: intent for index, intent in enumerate(intent_data.keys())}
        logging.info("Index-to-intent mapping created.")

        self.fafsa_eligible = FAFSAEligibilityFlow()
        self.student_fsaid = StudentFafsa()
        self.parent_fsaid = ParentFafsa()
        self.which_parent_fsaid = WhichParentFSAID()
        self.independent = IndependentFSAID()
        self.which_parent_invite = WhichParentInvite()
        logging.info('Flows Initialized')

        self.sms_handler = SMSHandler(api_url=FAFSA_SERVER_URL)

    def _get_training_texts(self):
        texts = []
        for intent, phrases in intent_data.items():
            texts.extend(phrases)
        return texts

    def classify_intent(self, message_body):
        with torch.no_grad():
            logging.info(f"Original message: {message_body}")

            text_tfidf = self.vectorizer.transform([message_body]).toarray()
            message_tensor = torch.tensor(text_tfidf, dtype=torch.float32)
            output = self.model(message_tensor)
            probabilities = torch.softmax(output, dim=1).numpy()[0]
            max_index = probabilities.argmax()
            intent = self.index_to_intent[max_index]  # Map index to intent
            confidence = probabilities[max_index]

        logging.info(f"Predicted intent: {intent} with confidence: {confidence:.4f}")
        return intent, confidence
    
    def get_active_flow_for_affirm_deny(self):
        flows = [
            self.fafsa_eligible,
            self.student_fsaid,
            self.which_parent_fsaid,
            self.independent,
            self.which_parent_invite,
            self.parent_fsaid
        ]
        for flow in flows:
            if flow.state != "START":
                return flow
        return None

    def handle_message(self, message_body, partner_id='default'):
        try:
            intent, confidence = self.classify_intent(message_body)
            logging.info(f"Handling intent: {intent} with confidence: {confidence:.4f}")

            confidence_threshold = 0.75

            if confidence < confidence_threshold:
                logging.info("Routing to Google System due to low confidence")
                return self.sms_handler.send_message_to_api(message_body, "conversation_uuid_placeholder")

            # First, check if there's a direct response available for the intent
            response_entry = get_qa_response(intent, partner_id)
            if response_entry:
                logging.info(f"Response from qa_responses for partner {partner_id}: {response_entry}")
                if isinstance(response_entry, dict):
                    response_text = response_entry.get('text', '')
                    response_image = response_entry.get('image', None)
                    response = [response_text]
                    if response_image:
                        response.append(response_image)
                    return response, intent, confidence
                else:
                    return [response_entry], intent, confidence

            intent_flow_mapping = {
                "fafsa_eligible": self.fafsa_eligible,
                "student_fsaid": self.student_fsaid,
                "which_parent_fsaid": self.which_parent_fsaid,
                "independent": self.independent,
                "which_parent_invite": self.which_parent_invite,
                "parent_fsaid": self.parent_fsaid,
                "affirm": self.get_active_flow_for_affirm_deny(),
                "deny": self.get_active_flow_for_affirm_deny(),
            }

            # Get the appropriate flow based on the intent
            flow = intent_flow_mapping.get(intent)

            if flow:
                response = flow.process_intent(intent, user_message=message_body, partner_id=partner_id)
                logging.info(f"Flow response: {response}")
                return response, intent, confidence
            
            try: 
                logging.info("Google system hit due to unmapped intent")
                response = self.sms_handler.send_message_to_api(message_body, "conversation_uuid_placeholder")
                logging.info(f"API response: {response}")
                return response
            except Exception as e:
                logging.error(f"An error occurred while sending the message to the API: {e}")
                return ["An error occurred. Please try again later."], intent, confidence
            
        except Exception as e:
                logging.error(f"An error occurred while handling the message: {e}")
                return ["An error occurred. Please try again later."], None, None
