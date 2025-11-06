from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionGetDataFromDb(Action):
    def name(self):
        return "action_get_data_from_db"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Get the account ID from the user slot
        account_id = tracker.get_slot("account_id_from_user")

        # --- Simulated Database Lookup ---
        # In production, this could be a DB query or API call.
        mock_db = {
            "EF1234": {"balance": 300.0, "owner_verified": True},
            "EF5678": {"balance": 150.0, "owner_verified": True},
            "ZZ9999": {"balance": 420.5, "owner_verified": False},
        }

        if account_id and account_id.upper() in mock_db:
            record = mock_db[account_id.upper()]
            check_access = record["owner_verified"]
            balance = record["balance"] if check_access else None

            # Return both slots
            return [
                SlotSet("check_access_status", check_access),
                SlotSet("balance", balance),
            ]
        else:
            # Account not found or invalid
            return [
                SlotSet("check_access_status", False),
                SlotSet("balance", None),
            ]
