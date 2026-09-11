# =========================================================
# Medical Report Analyzer — Backend Constants
# No magic strings. All shared literals live here.
# =========================================================

# Authentication
TOKEN_TYPE = "bearer"
AUTH_SCHEME = "Bearer"

# User role constants (prepared for future RBAC)
ROLE_USER = "user"
ROLE_ADMIN = "admin"

# Report status values
class ReportStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Medical value status labels
class MedicalValueStatus:
    NORMAL = "normal"
    HIGH = "high"
    LOW = "low"
    CRITICAL = "critical"

# File type constants (Phase 2)
class FileType:
    PDF = "pdf"
    IMAGE = "image"
    TXT = "txt"

ALLOWED_FILE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

# API Versions
API_V1 = "v1"

# Pagination defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
