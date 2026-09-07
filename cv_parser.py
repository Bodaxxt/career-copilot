"""
CareerHub AI - Root CV Parser Module
يقوم بإعادة تصدير الدوال من حزمة utils.cv_parser لضمان التوافقية الشاملة.
"""

from utils.cv_parser import (
    parse_cv,
    parse_cv_from_text,
    extract_raw_text_from_pdf,
    get_gemini_api_key,
    CV_EXTRACTION_PROMPT,
    MAX_FILE_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
    DEFAULT_MODEL,
)

__all__ = [
    "parse_cv",
    "parse_cv_from_text",
    "extract_raw_text_from_pdf",
    "get_gemini_api_key",
    "CV_EXTRACTION_PROMPT",
    "MAX_FILE_SIZE_MB",
    "MAX_FILE_SIZE_BYTES",
    "DEFAULT_MODEL",
]
