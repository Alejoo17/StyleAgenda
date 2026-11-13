class StyleAgendaError(Exception):
    """Base para errores de negocio."""


class NotFoundError(StyleAgendaError):
    pass


class ConflictError(StyleAgendaError):
    pass


class ValidationError(StyleAgendaError):
    pass
