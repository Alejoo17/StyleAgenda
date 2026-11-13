from app.domain.notifications.appointment_subject import AppointmentSubject
from app.infrastructure.notifications.email_listener import EmailListener
from app.infrastructure.notifications.log_listener import LogListener


def appointment_subject() -> AppointmentSubject:
    subject = AppointmentSubject()
    subject.attach(EmailListener())
    subject.attach(LogListener())
    return subject
