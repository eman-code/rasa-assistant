from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionHandleConfirmation(Action):
    def name(self):
        return "action_handle_confirmation"

    def run(self, dispatcher, tracker, domain):
        confirm = tracker.get_slot("confirm_recap")

        if confirm:
            dispatcher.utter_message(response="utter_confirm_success")
        else:
            dispatcher.utter_message(response="utter_handoff")
        return []
