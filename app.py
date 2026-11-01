
import os
import secrets
import csv
import io
import re
import sqlite3

from pathlib import Path
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from message_processor import classify_message, detect_device
from actions import (
    start_pricing_conversation,
    continue_pricing_conversation
)

app = FastAPI(title="NEXORA AI")

# Serve frontend files.
app.mount("/static", StaticFiles(directory="static"), name="static")


# =========================================
# EARLY ACCESS DATABASE
# =========================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "early_access.db"


def initialize_database():

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        # Create the registration table if it doesn't exist.
        
        # Create the registration activity history table.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL,
                old_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (registration_id)
                    REFERENCES early_access(id)
            )
        """)


        # Check whether the status column already exists.
        cursor.execute("PRAGMA table_info(early_access)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add the status column if it's missing.
        if "status" not in columns:
            cursor.execute("""
                ALTER TABLE early_access
                ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'
            """)

        connection.commit()


initialize_database()
   


# Display the NEXORA AI landing page.
@app.get("/")
def home():
    return FileResponse("static/index.html")


# Display the preserved computer repair assistant.
@app.get("/assistant")
def assistant():
    return FileResponse("static/assistant.html")


# =========================================
# EARLY ACCESS REGISTRATION
# =========================================
class RegistrationStatusUpdate(BaseModel):
    status: str

class EarlyAccessRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    account_type: str


@app.post("/early-access")
def register_early_access(request: EarlyAccessRequest):

    full_name = request.full_name.strip()
    email = request.email.strip().lower()
    account_type = request.account_type.strip()

    if len(full_name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Please enter your full name."
        )

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(
            status_code=422,
            detail="Please enter a valid email address."
        )

    if account_type not in ["Individual", "Freelancer", "Business"]:
        raise HTTPException(
            status_code=422,
            detail="Please select a valid account type."
        )

    try:
        with sqlite3.connect(DATABASE) as connection:
            connection.execute(
                """
                INSERT INTO early_access
                (full_name, email, account_type)
                VALUES (?, ?, ?)
                """,
                (full_name, email, account_type)
            )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="This email address has already been registered."
        )

    return {
        "success": True,
        "message": "Your early-access request has been received!"
    }


# =========================================
# CHAT ASSISTANT
# =========================================

# Store customer conversations.
conversations = {}


class ChatMessage(BaseModel):
    session_id: str
    message: str


def handle_other_requests(category, message):

    if category == "booking":
        return "I can help you with a repair appointment. Booking functionality is not set up yet."

    elif category == "technical support":
        device = detect_device(message)

        if device != "unknown":
            return f"I see you're having a problem with your {device}. Let's work through it."

        return "What device are you having a problem with: laptop, desktop, or printer?"

    elif category == "business information":
        return "I can help with our shop information, but the address and business details still need to be configured."

    return "Thank you for contacting us! How can I help you today?"


@app.post("/chat")
def chat(request: ChatMessage):

    session_id = request.session_id
    message = request.message.lower().strip()

    if not message:
        return {"response": "Please enter a message."}

    conversation = conversations.get(session_id)

    # Start a new conversation or handle a new request.
    if conversation is None:

        category = classify_message(message)

        if category == "pricing":
            conversation, response = start_pricing_conversation(message)

        else:
            response = handle_other_requests(category, message)

    # Continue an existing conversation.
    else:

        if (
            conversation["state"] == "waiting_for_device"
            and detect_device(message) != "unknown"
        ):
            conversation, response = continue_pricing_conversation(
                message, conversation
            )

        else:
            category = classify_message(message)

            if category == "pricing":
                conversation, response = start_pricing_conversation(message)

            elif category != "general inquiry":
                conversation = None
                response = handle_other_requests(category, message)

            else:
                conversation, response = continue_pricing_conversation(
                    message, conversation
                )

    # Save the updated conversation.
    conversations[session_id] = conversation

    return {"response": response}

# =========================================
# ADMIN AUTHENTICATION
# =========================================

security = HTTPBasic()


def require_admin(
    credentials: HTTPBasicCredentials = Depends(security)
):
    admin_password = os.getenv("NEXORA_ADMIN_PASSWORD")

    if not admin_password:
        raise HTTPException(
            status_code=503,
            detail="Admin password is not configured."
        )

    correct_username = secrets.compare_digest(
        credentials.username,
        "admin"
    )

    correct_password = secrets.compare_digest(
        credentials.password,
        admin_password
    )

    if not correct_username or not correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin username or password.",
            headers={"WWW-Authenticate": "Basic"}
        )

    return True

# =========================================
# ADMIN REGISTRATION MANAGEMENT
# =========================================


def get_registrations(search="", status="All"):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        query = """
            SELECT id, full_name, email, account_type,
                   created_at, status
            FROM early_access
            WHERE 1=1
        """

        parameters = []

        # Search by name or email.
        if search:
            keyword = f"%{search}%"
            query += """
                AND (full_name LIKE ? OR email LIKE ?)
            """
            parameters.extend([keyword, keyword])

        # Filter by registration status.
        if status in ["Pending", "Approved", "Rejected"]:
            query += " AND status = ?"
            parameters.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, parameters)

        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()


        
@app.get("/admin/statistics")
def admin_statistics(
    authenticated: bool = Depends(require_admin)
):
    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END)
            FROM early_access
        """)

        result = cursor.fetchone()

        return {
            "total": result[0] or 0,
            "pending": result[1] or 0,
            "approved": result[2] or 0,
            "rejected": result[3] or 0
        }

    finally:
        connection.close()



@app.get(
    "/admin",
    dependencies=[Depends(require_admin)]
)
def admin_page():
    return FileResponse("static/admin.html")


@app.get("/admin/registrations")
def admin_registrations(
    q: str = "",
    status: str = "All",
    authenticated: bool = Depends(require_admin)
):
    return get_registrations(q.strip(), status)


@app.get("/admin/export.csv")
def export_registrations(
    authenticated: bool = Depends(require_admin)
):
    registrations = get_registrations()

    output = io.StringIO(newline="")
    writer = csv.writer(output)

    writer.writerow([
    "ID",
    "Full Name",
    "Email",
    "Account Type",
    "Registration Date",
    "Status"
])

    for registration in registrations:
        writer.writerow([
            registration["id"],
            registration["full_name"],
            registration["email"],
            registration["account_type"],
            registration["created_at"],
            registration["status"]
        ])

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=nexora-registrations.csv"
        }
    )
 

@app.patch("/admin/registrations/{registration_id}/status")
def update_registration_status(
    registration_id: int,
    request: RegistrationStatusUpdate,
    authenticated: bool = Depends(require_admin)
):
    if request.status not in ["Pending", "Approved", "Rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid registration status."
        )

    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.cursor()

        # Get the current status before changing it.
        cursor.execute("""
            SELECT status
            FROM early_access
            WHERE id = ?
        """, (registration_id,))

        registration = cursor.fetchone()

        if registration is None:
            raise HTTPException(
                status_code=404,
                detail="Registration not found."
            )

        old_status = registration[0]

        # Avoid recording changes when the status is unchanged.
        if old_status == request.status:
            return {
                "success": True,
                "message": "Registration status is unchanged."
            }

        # Update the registration status.
        cursor.execute("""
            UPDATE early_access
            SET status = ?
            WHERE id = ?
        """, (request.status, registration_id))

        # Record the status change.
        cursor.execute("""
            INSERT INTO registration_history (
                registration_id,
                old_status,
                new_status
            )
            VALUES (?, ?, ?)
        """, (
            registration_id,
            old_status,
            request.status
        ))

        connection.commit()

        return {
            "success": True,
            "message": f"Registration {request.status.lower()}.",
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

@app.get("/admin/registration-history")
def get_registration_history(
    authenticated: bool = Depends(require_admin)
):
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                h.id,
                h.registration_id,
                e.full_name,
                e.email,
                h.old_status,
                h.new_status,
                h.changed_at
            FROM registration_history AS h
            JOIN early_access AS e
                ON h.registration_id = e.id
            ORDER BY h.changed_at DESC, h.id DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()
