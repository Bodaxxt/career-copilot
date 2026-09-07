import io
import json
import unittest
from unittest.mock import MagicMock, patch
from google.api_core import exceptions as google_exceptions

import utils.cv_parser as cv_parser
from utils.cv_parser import (
    parse_cv,
    parse_cv_from_text,
    extract_raw_text_from_pdf,
    MAX_FILE_SIZE_BYTES
)


class MockUploadedFile:
    """كائن يحاكي ملف مرفوع من st.file_uploader"""
    def __init__(self, name: str, content: bytes, file_type: str = ""):
        self.name = name
        self._content = content
        self.size = len(content)
        self.type = file_type
        self._buffer = io.BytesIO(content)

    def read(self, *args):
        return self._buffer.read(*args)

    def getvalue(self):
        return self._content

    def seek(self, pos):
        return self._buffer.seek(pos)


class TestCVParser(unittest.TestCase):

    @patch("utils.cv_parser.extract_raw_text_from_pdf", return_value=("نص تجريبي سيرة ذاتية", None))
    @patch("utils.cv_parser.get_gemini_api_key", return_value="fake_api_key_123")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_valid_pdf_success(self, mock_configure, mock_model_class, mock_key, mock_extract):
        """الحالة 1: ملف PDF صالح والـ API يرجع كائن Dict سليم بالمخطط المطلوب"""
        expected_cv_dict = {
            "full_name": "سارة أحمد",
            "headline": "مهندسة بيانات",
            "summary": "متخصصة في بناء خطوط معالجة البيانات وتحليلها",
            "skills": ["Python", "Sql", "Apache spark", "Docker"],
            "experiences": [
                {
                    "company": "بيانات للحلول",
                    "title": "مهندسة بيانات أولى",
                    "period": "2022-01 إلى current",
                    "achievements": ["بناء ETL pipelines", "تقليل زمن الاستعلام بنسبة 40%"]
                }
            ],
            "education": [
                {
                    "university": "جامعة الملك فهد",
                    "degree": "بكالوريوس",
                    "field": "علوم الحاسب",
                    "year": "2021"
                }
            ],
            "projects": [
                {
                    "name": "منصة تدفق البيانات",
                    "technologies": ["Kafka", "Spark"],
                    "description": "معالجة تدفقات البيانات لحظياً"
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(expected_cv_dict, ensure_ascii=False)
        
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        fake_pdf = MockUploadedFile("my_resume.pdf", b"%PDF-1.4 fake pdf content...", "application/pdf")
        
        result_dict, raw_text, error_msg = parse_cv(fake_pdf)
        
        self.assertIsNotNone(result_dict)
        self.assertIsNone(error_msg)
        self.assertEqual(raw_text, "نص تجريبي سيرة ذاتية")
        self.assertEqual(result_dict["full_name"], "سارة أحمد")
        self.assertEqual(result_dict["skills"], ["Python", "Sql", "Apache spark", "Docker"])

    def test_non_pdf_file_rejection(self):
        """الحالة 2: رفض الملفات التي ليست بصيغة PDF"""
        docx_file = MockUploadedFile("resume.docx", b"PK fake docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        result_dict, raw_text, error_msg = parse_cv(docx_file)
        
        self.assertIsNone(result_dict)
        self.assertIsNotNone(error_msg)
        self.assertIn("نوع الملف غير مدعوم", error_msg)

    def test_oversized_file_rejection(self):
        """الحالة 3: رفض الملفات التي تتجاوز الحد الأقصى للحجم (10MB)"""
        large_size = MAX_FILE_SIZE_BYTES + 1024
        large_pdf = MockUploadedFile("large_cv.pdf", b"0" * 100, "application/pdf")
        large_pdf.size = large_size

        result_dict, raw_text, error_msg = parse_cv(large_pdf)
        
        self.assertIsNone(result_dict)
        self.assertIn("يتجاوز الحد الأقصى", error_msg)

    def test_empty_file_rejection(self):
        """الحالة 4: رفض الملف الفارغ (0 بايت)"""
        empty_pdf = MockUploadedFile("empty.pdf", b"", "application/pdf")
        result_dict, raw_text, error_msg = parse_cv(empty_pdf)
        
        self.assertIsNone(result_dict)
        self.assertIn("فارغ", error_msg)

    @patch("utils.cv_parser.extract_raw_text_from_pdf", return_value=("نص تجريبي", None))
    @patch("utils.cv_parser.get_gemini_api_key", return_value="fake_api_key_123")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_rate_limit_fallback_flow(self, mock_configure, mock_model_class, mock_key, mock_extract):
        """الحالة 5: اختبار آلية التعافي عند حدوث خطأ كوتا أو تجاوز المعدل (Rate Limit 429)"""
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = google_exceptions.ResourceExhausted("Rate limit exceeded")
        mock_model_class.return_value = mock_model_instance

        fake_pdf = MockUploadedFile("cv.pdf", b"%PDF-1.4 content", "application/pdf")
        result_dict, raw_text, error_msg = parse_cv(fake_pdf)
        
        self.assertIsNone(result_dict)
        self.assertEqual(raw_text, "نص تجريبي")
        self.assertIn("Rate Limit", error_msg)


if __name__ == "__main__":
    unittest.main()
