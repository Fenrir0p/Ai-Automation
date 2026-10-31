
from message_processor import detect_device
from business_data import SERVICE_CATALOG


def find_service(message):
    # Search for a service using its registered keywords.
    for service in SERVICE_CATALOG.values():
        for keyword in service["keywords"]:
            if keyword in message:
                return service

    return None


def get_pricing_response(selected_service, device):
    # Retrieve the prices for the selected service.
    prices = selected_service["prices"]

    # Check if the device has an available price.
    if device not in prices:
        return (
            f"{selected_service['name']} is not listed "
            f"for {device} in our service catalog. "
            "Please contact the shop for assistance."
        )

    # Retrieve and display the price.
    price = prices[device]

    return (
        f"Our {selected_service['name']} service "
        f"for your {device} costs PHP {price:,}."
    )


def start_pricing_conversation(message):
    selected_service = find_service(message)
    device = detect_device(message)

    conversation = {
        "state": None,
        "service": selected_service
    }

    # Check whether the service was identified.
    if selected_service is None:
        conversation["state"] = "waiting_for_service"

        response = (
            "I can provide prices for device cleaning, "
            "diagnostics, and Windows installation. "
            "Which service do you need?"
        )

    # Check whether the device was identified.
    elif device == "unknown":
        conversation["state"] = "waiting_for_device"

        response = (
            f"Our service is {selected_service['name']}. "
            "Is your device a laptop, desktop, or printer?"
        )

    # Both service and device are available.
    else:
        response = get_pricing_response(selected_service, device)
        conversation = None

    return conversation, response


def continue_pricing_conversation(answer, conversation):

    # The assistant is waiting for the service name.
    if conversation["state"] == "waiting_for_service":
        selected_service = find_service(answer)

        if selected_service is None:
            return conversation, (
                "I couldn't identify that service. "
                "Please choose device cleaning, diagnostics, "
                "or Windows installation."
            )

        conversation["service"] = selected_service
        device = detect_device(answer)

        if device == "unknown":
            conversation["state"] = "waiting_for_device"

            return conversation, (
                f"Our service is {selected_service['name']}. "
                "Is your device a laptop, desktop, or printer?"
            )

        return None, get_pricing_response(selected_service, device)

    # The assistant is waiting for the device type.
    elif conversation["state"] == "waiting_for_device":
        device = detect_device(answer)

        if device == "unknown":
            return conversation, (
                "I didn't recognize that device. "
                "Please enter laptop, desktop, or printer."
            )

        selected_service = conversation["service"]

        return None, get_pricing_response(selected_service, device)


def handle_request(category, message):

    if category == "booking":
        print("Trigger: Start booking process")

    elif category == "technical support":
        device = detect_device(message)

        if device != "unknown":
            print("Device:", device)

        print("Trigger: Start troubleshooting process")

    elif category == "business information":
        print("Trigger: Retrieve business information")

    else:
        print("Trigger: Send to general inquiry process")
