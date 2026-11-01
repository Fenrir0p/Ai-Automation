
from message_processor import classify_message, detect_device
from actions import (
    handle_request,
    start_pricing_conversation,
    continue_pricing_conversation
)


conversation = None

while True:

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

        if category == "pricing":
            conversation, response = start_pricing_conversation(message)
            print("Assistant:", response)
        else:
            handle_request(category, message)

    else:
        answer = input("\nCustomer: ").lower().strip()

        if answer == "exit":
            print("Assistant: Thank you for contacting us!")
            break

        if not answer:
            continue

        # Check whether the customer supplied the requested device.
        if (
            conversation["state"] == "waiting_for_device"
            and detect_device(answer) != "unknown"
        ):
            conversation, response = continue_pricing_conversation(
                answer, conversation
            )

        else:
            category = classify_message(answer)

            # Customer wants to ask about a different pricing service.
            if category == "pricing":
                conversation, response = start_pricing_conversation(answer)

            # Customer wants to switch to another request.
            elif category != "general inquiry":
                conversation = None
                print("Category:", category)
                handle_request(category, answer)
                continue

            # The answer may be an invalid device or service.
            else:
                conversation, response = continue_pricing_conversation(
                    answer, conversation
                )

        print("Assistant:", response)
