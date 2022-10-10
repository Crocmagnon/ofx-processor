from ofx_processor.senders import sms, email, telegram, home_assistant

SENDERS = {
    "sms": sms.send,
    "email": email.send,
    "telegram": telegram.send,
    "home_assistant": home_assistant.send,
}
