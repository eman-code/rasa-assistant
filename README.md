# Take home exercise

- A bot is already built and some additional functionalities are needed (Rasa version to install is 3.11.4)

- in the credentials file you can find two models, feel free to use either one

- one model fine tuned by Rasa `rasa/cmd_gen_codellama_13b_calm_demo`

- gpt-4 (if you have access)

  

- Create a public repository and add the current bot to it.

-  `Train` the assistant and run `rasa inspect` to talk to it. This will help you understand its current functionalities.

- Do not hesitate to run the end-to-end test cases with `rasa test e2e tests/e2e_test_cases -o` (add the environment variable `RASA_PRO_BETA_E2E_ASSERTIONS=true`)

- The goal is that the conversation below will work after your changes. You will be presenting this conversation in `rasa inspect` view with the interviewer. The bot responses *must be identical* to the conversation captured in the screen shots below

- The changes required could include:

- add new flows

- adjust existing functionalities

- customise patterns

- adjust the prompt

- create custom actions ...

  

![](./images/image1.png)

![](./images/image2.png)

![](./images/image3.png)

![](./images/image4.png)

![](./images/image5.png)

  

![](./images/image6.png)

  
  

# Ideas to make the bot closer to real world scenarios:

## Use of Agents and LLMs

1. Moving from a conversational script to a reasoning system. A usecase: multi-intent conversations; Instead of pre-defining every conversational turn in YAML flows, use a powerful LLM (like GPT-4, Gemini, etc) as a "reasoning engine."

- Details:

	- User says: "What's my checking account balance and what were my last three transactions?"
	- Rasa/LLM NLU: Extracts key entities (checking account, balance, last three transactions).
	- The Agent (LLM): Receives the user’s request and a list of available "tools" ( custom actions). It thinks, step-by-step:
		- "The user wants two things. First, the balance. I need the get_balance tool for that."
		- "The get_balance tool requires an account_type. I have that: 'checking'."
		- Action 1: The agent instructs Rasa to execute 	action_get_balance(account_type='checking').
		- Result 1: The action returns "balance": 1234.56.
		- The Agent thinks: "Okay, I have the balance. Now I need the transactions. I need the get_transaction_history tool."
"This tool requires account_type and limit. I have both: 'checking' and '3'."
		- Action 2: The agent instructs Rasa to execute action_get_transaction_history(account_type='checking', limit=3).
		- Result 2: The action returns a list of transactions.
		- The Agent thinks: "I have all the information. Now I will generate a single, natural language response for the user."
	- Final Response (GenAI): The LLM synthesizes the data from both tool calls into one cohesive answer: "Your checking account balance is $1,234.56. Your last three transactions were a $50 payment to Amazon, a $15 coffee purchase, and a $1,000 deposit."

  

2. Dynamic, Generative Responses (NLG) with prompt engineering: Move beyond static utter_ templates. Use an LLM to rephrase responses, making the bot sound less robotic.

	- Details: Create a custom action action_generate_response. Instead of calling utter_provide_balance, your flow would call this action, passing it the core information (balance: 1234.56) and a prompt like: "Politely inform the user their balance is {balance}. Use a friendly and professional tone."

  

3. Conversation Summarization for Handoff: When a user is handed off to a human agent, the human often has no context.

	- Details: Before linking to the handoff flow, trigger a custom action that takes the conversation history from the Rasa tracker and sends it to an LLM with the prompt: "Summarize this customer's issue in 3 bullet points for a support agent. The user's goal was to check their balance but they could not authenticate." This summary is then passed directly to the human agent's chat window, saving significant time.

## Maintenance and scalability
1. CI/CD for Conversational AI (MLOps): Automate the entire process of testing, training, and deploying this bot.
	- Details:
		* Automated Testing: A CI pipeline automatically runs rasa test on every commit to ensure you haven't broken existing conversations.
		* Automated Training & Deployment: On a successful merge to the main branch, the pipeline automatically triggers rasa train, versions the new model, and deploys it to a staging environment for final review before pushing to production.

2. Modular and Microservice Architecture: Do not build a single, monolithic bot. Break it down.
	- Details:
		* Separate Domain Files
		* Separate Action Servers: One for "Account Services," one for "Card Services," etc. This makes them easier to maintain and scale independently.
		* Flows as Modules: Keep flows small and focused on a single task. Use the link step to connect them, treating them like functions in a program.
 
3. Caching and Performance Optimization: Reduce latency and API costs.
	- Details:
		* MemoizationPolicy
		* External Caching: For expensive, non-real-time data (e.g., a list of branch locations), your custom action can cache the results for a few hours. This prevents repeated API calls for the same static information.
		* Stateless Action Server: Design the custom actions to be stateless. They should get all the information they need from the tracker. This allows you to run multiple, load-balanced instances of the action server for high-traffic scenarios.

## Security:
1. Implement User Authentication. Must verify the user's identity before accessing their data.
	- Details:
		* Before checking the balance, start with a login step. Ask for a unique identifier like a customer_id or username.
		* Create a custom action (action_authenticate_user) that prompts for a password or, even better, triggers a Two-Factor Authentication (2FA) process.
		* The action could send a code to the user's registered phone/email and the flow would then collect the 2fa_code from the user. Only after successful validation would the bot proceed.
		* 
2. Create a Reusable Authentication Flow: Many banking tasks (transfer money, pay bills, check balance) will require the same authentication. Don't repeat the logic.
	- Details: Create a dedicated authentication_flow.yml. Other flows like check_balance would start with a link: authentication_flow step. The authentication flow would set a slot like is_authenticated: true, which other flows can then check.

## Improving User Experience and Error Handling:
1. Differentiate "Account Not Found" from "Access Denied": Your current flow has one failure message: "you don't own this account". But what if the account number doesn't exist at all? The message should be different.
	- Details: Your custom action action_get_data_from_db should return more specific statuses. Instead of just a boolean check_access_status, it could return a text slot data_retrieval_status with values like "SUCCESS", "ACCESS_DENIED", or "NOT_FOUND". Your flow can then have different branches for each status, providing much clearer feedback to the user.
	
2. Validate the Account Number Format: A user might accidentally type "hello" or a number that's too short/long. You can catch this error immediately instead of making a pointless database call.
	- Details: Use a Validation Action on the account_id_from_user slot. In the validation code, you can use a regular expression to check if the input matches the format of a real account number. If it doesn't, you can reject the input and ask the user to try again with a helpful hint.
	
3. Handle Multiple Accounts: A single customer often has multiple accounts (e.g., checking, savings, credit card).
	- Details:
		* action_get_customer_info should return a list of account numbers associated with the authenticated user.
		* The flow should then check if the list has more than one account.
		* If yes, use an utter_ask_which_account response with buttons for each account number, allowing the user to choose easily.

4. Implement a Confirmation Step: To prevent errors from typos, etc confirm the information you've collected before acting on it.
	- Details: After the user provides an account_id_from_user, add a step: - action: utter_confirm_account_id with a text like: "Got it. Just to confirm, the account number is {account_id_from_user}, correct?" and "Yes/No" buttons.

5. Allow for FAQ in the middle. In the middle of providing their account number, a user might ask, "What are your business hours?" A good bot should answer the question and then seamlessly return to the flow.
	- Details: Ensure there are flows that can handle common off-topic questions (FAQs) and that the policies (like RulePolicy) are configured to allow these interruptions without breaking the flow.

## Expanding Functionality and Proactive Assistance
1. Offer Proactive "Next Steps": After a user gets their balance, their next goal is often to use that information (e.g., pay a bill, transfer money). Don't make them start over.
	- Details: After the utter_provide_balance action, instead of ending the flow, add another action: utter_ask_next_step with a text like "Now that you have your balance, is there anything else I can help you with?" and provide buttons like "Make a Transfer", "Pay a Bill", or "No, I'm done".

2. Add a Follow-Up for Transaction History: "What are my recent transactions?" is the most common follow-up question to "What is my balance?".
	- Details: In the "Next Steps" mentioned above, one of the buttons could be "See Recent Transactions". This would link to a new transaction_history_flow.

3. Proactive Notifications and Engagement: A bot shouldn't just wait for questions. It can initiate conversations based on backend triggers.
	- Details: Connect the bot to your core banking system's event stream (here the db we have).
		* Low Balance Alert: If a user's balance drops below a threshold, the bot can proactively message them: "Hi [Name], just a friendly alert that your checking account balance is now $25. Would you like to set up a transfer?"
		* Fraud Alert: "We've detected an unusual transaction of $500 in a different country. Was this you?" (with "Yes/No" buttons).

## Deep Personalization:

1. Treat the user like an individual, not a generic query source.

	- Details: Your action_get_customer_info should retrieve more than just an account number. It should get their name, preferred language, and maybe even a "customer value" score. The flow can then use this data:

2. Prioritization: If a high-value customer is struggling, the handoff to a human agent can be prioritized.
	- Details: Novice/ Expert user: is the user usually comfortable handling multiple tasks together or the sequential execution is preferred.

## Multimodal Experience:

1. The user's conversation should persist across different channels (web chat, mobile app, Facebook).
	- Details: When a user logs in on the mobile app, the bot can retrieve their existing conversation from their web chat session and say, "Welcome back! We were just talking about your account balance. Shall we continue?"

## Reliability:
1. Use a More Reliable Slot Mapping: from_llm can sometimes be unpredictable for structured, critical data like an account number. from_text with entity extraction is more robust.
	- Details:
		In domain, define a account_number entity.
		In config.yml, add a RegexEntityExtractor that can reliably find account number patterns in the user's message.
		Change the mapping for the account_id_from_user slot from type: from_llm to type: from_entity and specify the entity: account_number.