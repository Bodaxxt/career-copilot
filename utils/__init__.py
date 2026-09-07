"""CareerHub AI Utilities Package"""

from .state_manager import (
    init_session_state,
    require_cv_profile,
    get_user_profile,
    set_user_profile,
    get_temp_draft_profile,
    set_temp_draft_profile,
    get_raw_pdf_text,
    set_raw_pdf_text,
    get_parse_status,
    set_parse_status,
    set_demo_mode,
    reset_session,
    DEMO_PROFILE_DATA,
)
from .cv_parser import (
    parse_cv,
    parse_cv_from_text,
    extract_raw_text_from_pdf,
    get_gemini_api_key,
    MAX_FILE_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
    DEFAULT_MODEL,
)

__all__ = [
    "init_session_state",
    "require_cv_profile",
    "get_user_profile",
    "set_user_profile",
    "get_temp_draft_profile",
    "set_temp_draft_profile",
    "get_raw_pdf_text",
    "set_raw_pdf_text",
    "get_parse_status",
    "set_parse_status",
    "set_demo_mode",
    "reset_session",
    "DEMO_PROFILE_DATA",
    "parse_cv",
    "parse_cv_from_text",
    "extract_raw_text_from_pdf",
    "get_gemini_api_key",
    "MAX_FILE_SIZE_MB",
    "MAX_FILE_SIZE_BYTES",
    "DEFAULT_MODEL",
]
