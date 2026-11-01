// =========================================
// NEXORA AI ADMIN PANEL
// =========================================

const registrationList = document.getElementById("registration-list");
const registrationCount = document.getElementById("registration-count");
const statusMessage = document.getElementById("status-message");

const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const clearSearch = document.getElementById("clear-search");
const statusFilter = document.getElementById("status-filter");


const viewHistoryButton =
    document.getElementById("view-history-button");

const hideHistoryButton =
    document.getElementById("hide-history-button");

const historySection =
    document.getElementById("history-section");

const historyList =
    document.getElementById("history-list");

const historyMessage =
    document.getElementById("history-message");



// =========================================
// LOAD REGISTRATIONS
// =========================================


// =========================================
// LOAD DASHBOARD STATISTICS
// =========================================

async function loadStatistics() {

    try {

        const response = await fetch("/admin/statistics");

        if (!response.ok) {
            throw new Error("Unable to load dashboard statistics.");
        }

        const statistics = await response.json();

        document.getElementById("total-count").textContent =
            statistics.total;

        document.getElementById("pending-count").textContent =
            statistics.pending;

        document.getElementById("approved-count").textContent =
            statistics.approved;

        document.getElementById("rejected-count").textContent =
            statistics.rejected;

    } catch (error) {

        console.error(error);

    }
}


async function loadRegistrations(search = "", status = "All")  {

    statusMessage.textContent = "Loading registrations...";
    registrationList.replaceChildren();

    try {

        const response = await fetch(
    `/admin/registrations?q=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`
);

        if (!response.ok) {
            throw new Error("Unable to load registrations.");
        }

        const registrations = await response.json();

        registrationCount.textContent =
            `${registrations.length} registration(s)`;

        if (registrations.length === 0) {
            statusMessage.textContent = "No registrations found.";
            return;
        }

        statusMessage.textContent = "";

        registrations.forEach(registration => {

            const row = document.createElement("tr");

            const values = [
                registration.id,
                registration.full_name,
                registration.email,
                registration.account_type,
                registration.created_at,
                registration.status
            ];

            values.forEach(value => {

                const cell = document.createElement("td");
                cell.textContent = value ?? "";

                row.appendChild(cell);

            });

            // Create action buttons.
            const actionCell = document.createElement("td");

           
            const statuses = ["Pending", "Approved", "Rejected"];

            statuses.forEach(status => {

                const button = document.createElement("button");

                button.textContent = status;
                button.className =
                    status === registration.status
                        ? "current-status-button"
                        : "status-action-button";

                button.disabled = status === registration.status;

                button.addEventListener("click", () => {
                    updateStatus(registration.id, status);
                });

                actionCell.appendChild(button);

            });


            row.appendChild(actionCell);

            registrationList.appendChild(row);

        });

    } catch (error) {

        statusMessage.textContent = error.message;
        registrationCount.textContent = "Unavailable";

    }
}


// =========================================
// UPDATE REGISTRATION STATUS
// =========================================

async function updateStatus(registrationId, newStatus) {

    const confirmed = window.confirm(
        `Are you sure you want to mark this registration as ${newStatus}?`
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/admin/registrations/${registrationId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Could not update registration.");
        }

        statusMessage.textContent = result.message;

        // Refresh the table to show the new status.
        await loadRegistrations(
        searchInput.value.trim(),
         statusFilter.value
        );

        await loadStatistics();

    } catch (error) {

        statusMessage.textContent = error.message;

    }
}


// =========================================
// SEARCH
// =========================================

searchForm.addEventListener("submit", function(event) {
    event.preventDefault();

    loadRegistrations(
        searchInput.value.trim(),
        statusFilter.value
    );
});


// =========================================
// CLEAR SEARCH
// =========================================

clearSearch.addEventListener("click", function() {
    searchInput.value = "";

    loadRegistrations("", statusFilter.value);
});


// =========================================
// INITIAL LOAD
// =========================================

loadRegistrations();
loadStatistics();

statusFilter.addEventListener("change", function() {
    loadRegistrations(
        searchInput.value.trim(),
        statusFilter.value
    );
});


// =========================================
// LOAD REGISTRATION HISTORY
// =========================================

async function loadRegistrationHistory() {

    historyMessage.textContent = "Loading activity history...";
    historyList.replaceChildren();

    try {

        const response = await fetch("/admin/registration-history");

        if (!response.ok) {
            throw new Error("Unable to load activity history.");
        }

        const history = await response.json();

        if (history.length === 0) {
            historyMessage.textContent = "No activity history found.";
            return;
        }

        historyMessage.textContent = "";

        history.forEach(record => {

            const row = document.createElement("tr");

            const values = [
                record.registration_id,
                record.full_name,
                record.email,
                record.old_status,
                record.new_status,
                record.changed_at
            ];

            values.forEach(value => {

                const cell = document.createElement("td");
                cell.textContent = value ?? "";

                row.appendChild(cell);

            });

            historyList.appendChild(row);

        });

    } catch (error) {

        historyMessage.textContent = error.message;

    }
}


// =========================================
// HISTORY BUTTONS
// =========================================

viewHistoryButton.addEventListener("click", async function() {

    historySection.hidden = false;

    await loadRegistrationHistory();

});

hideHistoryButton.addEventListener("click", function() {

    historySection.hidden = true;

});
