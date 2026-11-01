# AI Customer Service Assistant

## 1. Project Overview

This project is a Python-based customer service assistant designed for a small computer repair business.

Its goal is to process customer messages, identify the type of inquiry, recognize relevant device information, and select an appropriate process for handling the request.

The project is being developed incrementally, starting with rule-based message processing before introducing more advanced AI capabilities and business integrations.

## 2. Current Features

- **Message Classification:** Categorizes customer messages as booking, technical support, pricing, business information, or general inquiry.
- **Device Detection:** Recognizes laptops, desktops, and printers when relevant to the request.
- **Conditional Information Display:** Avoids displaying unknown or irrelevant device information.
- **Trigger Selection:** Selects a process based on the message category.
- **Modular Code Structure:** Separates message processing, action handling, and program execution into different files.

## 3. Project Structure

```text
ai-automation-starter/
├── main.py
├── message_processor.py
├── actions.py
└── README.md
```

### File Responsibilities

- `main.py` — Receives the customer's message and coordinates the program.
- `message_processor.py` — Classifies messages and detects devices.
- `actions.py` — Selects the process associated with the message category.
- `README.md` — Documents the project and its development.

## 4. Requirements

- Python 3.15 or a compatible Python version.
- A code editor such as Visual Studio Code.

The current implementation uses Python's built-in functionality and does not require external Python packages.

## 5. How to Run

Open a terminal in the project directory and execute:

```powershell
py main.py
```

Enter a customer message when prompted.

## 6. Example Usage

Example customer message:

```text
I want to book a desktop repair.
```

Expected output:

```text
You entered: i want to book a desktop repair.
Category: booking
Device: desktop
Trigger: Start booking process
```

Another example:

```text
Where is your business located?
```

Expected output:

```text
You entered: where is your business located?
Category: business information
Trigger: Retrieve business information
```

## 7. Current Limitations

- Message classification relies on predefined keywords.
- Messages with unfamiliar wording may be classified incorrectly.
- Device detection recognizes only predefined device names.
- Trigger selection currently prints a message rather than performing a real business action.
- The assistant does not yet maintain customer records or schedule appointments.

## 8. Planned Development

Potential future improvements include:

1. Improving message classification and handling multiple requests.
2. Extracting relevant information, such as devices, services, and appointment details.
3. Asking follow-up questions when customer information is missing.
4. Connecting triggers to real business processes.
5. Storing customer requests and records.
6. Integrating email, calendar services, and AI-powered message understanding.

Features will be marked as complete only after implementation and testing.