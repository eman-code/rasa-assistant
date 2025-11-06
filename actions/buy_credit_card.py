from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionSaveCreditCardRequest(Action):
    def name(self):
        return "action_save_credit_card_request"

    def run(self, dispatcher, tracker, domain):
        card_type = tracker.get_slot("credit_card_type")
        delivery_type = tracker.get_slot("delivery_type")
        address = tracker.get_slot("address")

        # Simulate persistence or API call
        print(f"[LOG] Saving credit card request: {card_type}, {delivery_type}, {address}")

        return []
