from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import logging

class ActionGetCustomerDataFromDB(Action):
    def name(self):
        return "action_get_data_from_db"
    
    def run(self, dispatcher, tracker, domain):
        #Load CSV file
        file_path = "db/customers_info.csv"  # get information from your DBs
        df = pd.read_csv(file_path)
        customer_id = tracker.get_slot("customer_id")
        account_id_from_user = str(tracker.get_slot("account_id_from_user"))
        logging.info(f"This is an info message: account_id_from_user: {account_id_from_user}")

        # Filter data for the given customer ID
        customer_info = df[df["customer_id"] == int(customer_id)]

        if customer_info.empty:
            dispatcher.utter_message("No customer found with this ID.")
            return []

        # Extract customer details
        account_id_from_db = str(customer_info.iloc[0]["account_id"])
        balance = customer_info.iloc[0]["balance"]
        logging.info(f"This is an info message: account_id_from_db: {account_id_from_db}")
        #dispatcher.utter_message(response)
        if account_id_from_db == account_id_from_user:
            print( "account_id_from_user: " + account_id_from_user +  "  account_id:" + account_id_from_db)
            return [ SlotSet("check_access_status",True),
                    SlotSet("balance",int(balance))]
        else:
            return [SlotSet("check_access_status",False)]
        