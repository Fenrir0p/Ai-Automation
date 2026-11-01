
// =========================================
// 1. MOBILE NAVIGATION
// =========================================

const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");

menuToggle.addEventListener("click", function () {

    const isOpen = navLinks.classList.toggle("active");

    menuToggle.setAttribute("aria-expanded", isOpen);

    menuToggle.textContent = isOpen ? "✕" : "☰";

});


// Close the mobile menu after selecting a link.

const navigationLinks = document.querySelectorAll(".nav-links a");

navigationLinks.forEach(function (link) {

    link.addEventListener("click", function () {

        navLinks.classList.remove("active");

        menuToggle.setAttribute("aria-expanded", "false");

        menuToggle.textContent = "☰";

    });

});


// =========================================
// 2. CURRENT YEAR
// =========================================

const currentYear = document.getElementById("current-year");

currentYear.textContent = new Date().getFullYear();


// =========================================
// 3. DEMO ELEMENTS
// =========================================

const demoForm = document.getElementById("demo-form");
const demoInput = document.getElementById("demo-input");
const demoMessages = document.getElementById("demo-messages");


// =========================================
// 4. DEMO RESPONSES
// =========================================

function generateDemoResponse(message) {

    const text = message.toLowerCase();

    if (
        text.includes("appointment") ||
        text.includes("booking") ||
        text.includes("schedule")
    ) {

        return `I can help you organize appointment requests.

A possible workflow would be:

1. Collect customer details.
2. Record preferred appointment times.
3. Prepare a confirmation for review.

This is an example of how an assistant could help manage appointments.`;

    }


    if (
        text.includes("document") ||
        text.includes("summarize") ||
        text.includes("summary")
    ) {

        return `I can help organize document-related tasks.

A possible workflow would be:

1. Receive the document.
2. Extract important information.
3. Create a concise summary.
4. Present the result for review.

Document processing is one of the capabilities we plan to develop.`;

    }


    if (
        text.includes("automate") ||
        text.includes("automation") ||
        text.includes("repetitive")
    ) {

        return `Let's look at a simple automation example.

Imagine receiving a customer request.

A workflow could:

1. Receive the request.
2. Identify its category.
3. Organize the information.
4. Notify the appropriate person.

The goal is to reduce repetitive manual work.`;

    }


    return `That's an interesting task!

NEXORA AI is being developed to support intelligent assistance and automation.

Try asking me about:

• Organizing appointments
• Summarizing documents
• Automating repetitive tasks

This demonstration currently supports only these sample topics.`;

}


// =========================================
// 5. DISPLAY DEMO MESSAGES
// =========================================

function addDemoMessage(message, sender) {

    const messageElement = document.createElement("div");

    messageElement.classList.add(
        "demo-message",
        sender === "customer"
            ? "customer-message"
            : "assistant-message"
    );

    messageElement.textContent = message;

    demoMessages.appendChild(messageElement);

    demoMessages.scrollTop = demoMessages.scrollHeight;

}


// =========================================
// 6. HANDLE DEMO SUBMISSION
// =========================================

function sendDemoMessage(message) {

    const cleanMessage = message.trim();

    if (!cleanMessage) {
        return;
    }

    addDemoMessage(cleanMessage, "customer");

    const response = generateDemoResponse(cleanMessage);

    addDemoMessage(response, "assistant");

}


// =========================================
// 7. DEMO FORM SUBMISSION
// =========================================

demoForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const message = demoInput.value.trim();

    if (!message) {
        return;
    }

    sendDemoMessage(message);

    demoInput.value = "";

    demoInput.focus();

});


// =========================================
// 8. SUGGESTED DEMO QUESTIONS
// =========================================

const suggestionButtons = document.querySelectorAll(
    ".suggestion-button"
);

suggestionButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        const message = button.dataset.message;

        sendDemoMessage(message);

    });

});


// =========================================
// 9. EARLY ACCESS REGISTRATION
// =========================================

const earlyAccessForm = document.getElementById(
    "early-access-form"
);

const earlyAccessMessage = document.getElementById(
    "early-access-message"
);

const earlyAccessButton = document.getElementById(
    "early-access-submit"
);


earlyAccessForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const registration = {
        full_name: document.getElementById("early-access-name").value.trim(),
        email: document.getElementById("early-access-email").value.trim(),
        account_type: document.getElementById("early-access-type").value
    };

    earlyAccessButton.disabled = true;
    earlyAccessButton.textContent = "Submitting...";

    earlyAccessMessage.textContent = "";
    
    try {

        const response = await fetch("/early-access", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(registration)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Registration failed.");
        }

        earlyAccessMessage.textContent = result.message;

        earlyAccessForm.reset();

    } catch (error) {

        earlyAccessMessage.textContent = error.message;

    } finally {

        earlyAccessButton.disabled = false;
        earlyAccessButton.textContent = "Request Early Access";

    }

});
