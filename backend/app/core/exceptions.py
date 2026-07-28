class AppError(Exception):
    status_code = 500
    detail = "Internal Server Error"

class ProjectNotFoundError(AppError):
    status_code = 404
    detail = "Project not found"

class DocumentNotFoundError(AppError):
    status_code = 404
    detail = "Document not found"

class InvalidDocumentUploadError(AppError):
    status_code = 415
    detail = "Invalid document format"

class QueueUnavailableError(AppError):
    status_code= 503
    detail = "Document uploaded but could not be queued for ingestion."