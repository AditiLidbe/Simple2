import json
from datetime import datetime

import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..model.appoinment_model import AppointmentStatus
from ..model.chat_model import ChatRole
from ..model.user_model import RoleEnum
from ..repo import appointment_repo, chat_repo
from ..utils.config import setting
from . import appointemnet_service as appointment_service


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_appointment_status",
            "description": "Check what is still missing for the patient's upcoming appointment.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_appointment",
            "description": "Move the patient's appointment to a new start time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_start_time": {
                        "type": "string",
                        "description": "New appointment start time in ISO 8601 format.",
                    }
                },
                "required": ["new_start_time"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_pre_visit_summary",
            "description": "Save the patient's plain-language concern as a neutral pre-visit summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Neutral summary for the clinician to read.",
                    }
                },
                "required": ["summary"],
                "additionalProperties": False,
            },
        },
    },
]


SYSTEM_PROMPT = (
    "You are the Threshold Intake Assistant for a clinic. "
    "Keep things simple and organized. Do not diagnose, triage, or give medical advice. "
    "If the request is unclear, ask one short clarifying question. "
    "If a tool says something failed, tell the patient plainly. "
    "Only work with the current patient. "
)


def _get_upcoming_appointment(db: Session, patient_id: int):
    appointments = appointment_repo.list_patient_appointments(db, patient_id)
    appointments = sorted(appointments, key=lambda item: item.date)

    for appointment in appointments:
        if appointment.status == AppointmentStatus.BOOKED:
            return appointment
        if appointment.status == AppointmentStatus.WAITING:
            return appointment
        if appointment.status == AppointmentStatus.CALLED_BACK:
            return appointment

    return None


def _missing_documents(appointment):
    missing = []

    # Check the simple intake fields first.
    existing_types = []
    for document in appointment.document:
        existing_types.append(document.document_type.value)

    if appointment.personal_details is None:
        missing.append("personal details")
    if appointment.medical_history is None:
        missing.append("medical history")
    if appointment.pre_visit_summary is None:
        missing.append("pre-visit summary")
    if "ID" not in existing_types:
        missing.append("ID document")
    if "INSURANCE" not in existing_types:
        missing.append("insurance card")
    if "PRIOR_RECORD" not in existing_types:
        missing.append("prior record")

    return missing


def execute_tool(name, tool_input, patient_id, db: Session):
    appointment = _get_upcoming_appointment(db, patient_id)
    if not appointment:
        return {"ok": False, "reason": "no_upcoming_appointment", "message": "No upcoming appointment was found."}

    if name == "get_appointment_status":
        result = {
            "ok": True,
            "appointment_id": appointment.id,
            "status": appointment.status,
            "intake_completed": bool(appointment.personal_details and appointment.medical_history),
            "missing_items": _missing_documents(appointment),
        }
        return result

    if name == "reschedule_appointment":
        new_start_time_text = tool_input.get("new_start_time", "")
        try:
            new_start_time = datetime.fromisoformat(new_start_time_text.replace("Z", "+00:00"))
        except Exception:
            return {"ok": False, "reason": "invalid_datetime", "message": "The date and time format was not valid."}

        try:
            updated_appointment = appointment_service.reschedule_appointment_service(db, appointment, new_start_time)
        except appointment_service.RescheduleError as exc:
            return {"ok": False, "reason": exc.reason, "message": exc.message}

        return {"ok": True, "new_start_time": updated_appointment.date.isoformat()}

    if name == "create_pre_visit_summary":
        summary = tool_input.get("summary", "").strip()
        if not summary:
            return {"ok": False, "reason": "empty_summary", "message": "The summary cannot be empty."}

        appointment.pre_visit_summary = summary
        appointment_repo.update_appointment(db, appointment)
        return {"ok": True}

    return {"ok": False, "reason": "unknown_tool", "message": "Unknown tool name."}


def get_chat_history(db: Session, appointment_id: int, patient_id: int):
    session = chat_repo.get_session_by_appointment(db, appointment_id, patient_id)
    if not session:
        return None
    return chat_repo.get_session_with_messages(db, session.id)


def _call_groq(messages):
    if not setting.GROQ_API_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GROQ_API_KEY is missing.")

    payload = {
        "model": setting.GROQ_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0.2,
    }

    response = requests.post(
        setting.GROQ_API_URL,
        headers={"Authorization": f"Bearer {setting.GROQ_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


def handle_assistant_message(db: Session, appointment, user, user_message: str):
    if user.role != RoleEnum.PATIENT or appointment.patient_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only use the assistant for your own appointment.")

    session = chat_repo.get_session_by_appointment(db, appointment.id, user.id)
    if not session:
        session = chat_repo.create_session(db, appointment.id, user.id)

    chat_repo.add_message(db, session.id, ChatRole.PATIENT, user_message)
    session = chat_repo.get_session_with_messages(db, session.id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in session.messages:
        if item.sender == ChatRole.PATIENT:
            messages.append({"role": "user", "content": item.message})
        elif item.sender == ChatRole.ASSISTANT:
            messages.append({"role": "assistant", "content": item.message})
        elif item.sender == ChatRole.TOOL:
            messages.append({"role": "tool", "content": item.message})

    while True:
        model_reply = _call_groq(messages)
        tool_calls = model_reply.get("tool_calls", [])

        if not tool_calls:
            text = model_reply.get("content", "")
            chat_repo.add_message(db, session.id, ChatRole.ASSISTANT, text)
            return text

        messages.append(model_reply)
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_arguments = tool_call["function"].get("arguments", "{}")
            tool_input = json.loads(tool_arguments)
            result = execute_tool(tool_name, tool_input, user.id, db)
            chat_repo.add_message(db, session.id, ChatRole.TOOL, json.dumps(result))
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result),
                }
            )
