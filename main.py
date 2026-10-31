
from message_processor import classify_message
from actions import (
    handle_request,
    start_pricing_conversation,
    continue_pricing_conversation
)


conversation = None

while True:

    # Start a new customer request.
    if conversation is None:
        message = input("\nCustomer: ").lower().strip()

        if message == "exit":
            print("Assistant: Thank you for contacting us!")
            break

        if not message:
            continue

        print("You entered:", message)

        category = classify_message(message)

        print("Category:", category)

        # Start the pricing conversation.
        if category == "pricing":
            conversation, response = start_pricing_conversation(message)

            print("Assistant:", response)

        # Handle other request categories.
        else:
            handle_request(category, message)

    # Continue an existing pricing conversation.
    else:
        answer = input("\nCustomer: ").lower().strip()

        if answer == "exit":
            print("Assistant: Thank you for contacting us!")
            break

        if not answer:
            continue

        conversation, response = continue_pricing_conversation(
            answer, conversation
        )

        print("Assistant:", response)
