def classify_message(message):
    if "book" in message or "appointment" in message:
        return "booking"

    elif "error" in message or "problem" in message:
        return "technical support"

    elif "price" in message or "cost" in message or "how much" in message:
        return "pricing"

    elif "location" in message or "address" in message or "where" in message:
        return "business information"

    else:
        return "general inquiry"


def detect_device(message):
    if "laptop" in message:
        return "laptop"

    elif "desktop" in message:
        return "desktop"

    elif "printer" in message:
        return "printer"

    else:
        return "unknown"
