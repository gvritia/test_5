from app.models.model_error import ErrorResponse


BAD_REQUEST = {
    400: {
        "model": ErrorResponse,
        "description": "Bad request or malformed JSON body.",
    }
}
UNAUTHORIZED = {
    401: {
        "model": ErrorResponse,
        "description": "Missing or invalid X-User-Id header.",
    }
}
FORBIDDEN = {
    403: {
        "model": ErrorResponse,
        "description": "The current user has no access to this resource.",
    }
}
NOT_FOUND = {
    404: {
        "model": ErrorResponse,
        "description": "The resource was not found.",
    }
}
VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Request validation error.",
    }
}
