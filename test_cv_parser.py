import io
import json
import unittest
from unittest.mock import MagicMock, patch
from google.api_core import exceptions as google_exceptions

import utils.cv_parser as cv_parser
from utils.cv_parser import parse_cv, MAX_FILE_SIZE_BYTES


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

    def setUp(self):
        # تعطيل أخطاء streamlit البصرية أثناء الاختبارات والتقاط الرسائل
        self.st_errors = []
        self.error_patcher = patch("streamlit.error", side_effect=lambda msg: self.st_errors.append(msg))
        self.error_patcher.start()

    def tearDown(self):
        self.error_patcher.stop()

    @patch("utils.cv_parser.get_gemini_api_key", return_value="fake_api_key_123")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_valid_pdf_success(self, mock_configure, mock_model_class, mock_key):
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
        
        # إعداد محاكاة النموذج
        mock_response = MagicMock()
        mock_response.text = json.dumps(expected_cv_dict, ensure_ascii=False)
        
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        fake_pdf = MockUploadedFile("my_resume.pdf", b"%PDF-1.4 fake pdf content...", "application/pdf")
        
        result_dict = parse_cv(fake_pdf)
        
        self.assertIsNotNone(result_dict)
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["full_name"], "سارة أحمد")
        self.assertEqual(result_dict["skills"], ["Python", "Sql", "Apache spark", "Docker"])
        self.assertEqual(result_dict["experiences"][0]["period"], "2022-01 إلى current")
        self.assertEqual(len(self.st_errors), 0)

    @patch("utils.cv_parser.get_gemini_api_key", return_value="fake_api_key_123")
    @patch("google.generativeai.GenerativeModel")
    def test_null_fields_preservation(self, mock_model_class, mock_key):
        """الحالة 2: التأكد من بقاء الحقول المفقودة كـ null وليس سلاسل فارغة"""
        cv_with_nulls = {
            "full_name": "خالد محمود",
            "headline": None,
            "summary": None,
            "skills": ["Javascript", "Node.js"],
            "experiences": [],
            "education": [
                {
                    "university": "جامعة دمشق",
                    "degree": None,
                    "field": "تقنية معلومات",
                    "year": "2019"
                }
            ],
            "projects": []
        }
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(cv_with_nulls, ensure_ascii=False)
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        fake_pdf = MockUploadedFile("cv.pdf", b"%PDF-1.4 content", "application/pdf")
        result_dict = parse_cv(fake_pdf)
        
        self.assertIsInstance(result_dict, dict)
        self.assertIsNone(result_dict["headline"])
        self.assertIsNone(result_dict["summary"])
        self.assertIsNone(result_dict["education"][0]["degree"])

    def test_non_pdf_file_rejection(self):
        """الحالة 3: رفض الملفات التي ليست بصيغة PDF (مثل docx أو png)"""
        docx_file = MockUploadedFile("resume.docx", b"PK fake docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        result = parse_cv(docx_file)
        
        self.assertIsNone(result)
        self.assertTrue(any("نوع الملف غير مدعوم" in err for err in self.st_errors))

    def test_oversized_file_rejection(self):
        """الحالة 4: رفض الملفات التي تتجاوز الحد الأقصى للحجم (10MB)"""
        large_size = MAX_FILE_SIZE_BYTES + 1024  # أكثر من 10MB
        large_pdf = MockUploadedFile("large_cv.pdf", b"0" * 100, "application/pdf")
        large_pdf.size = large_size  # محاكاة الحجم الكبير

        result = parse_cv(large_pdf)
        
        self.assertIsNone(result)
        self.assertTrue(any("يتجاوز الحد" in err for err in self.st_errors))

    def test_empty_file_rejection(self):
        """الحالة 5: رفض الملف الفارغ (0 بايت)"""
        empty_pdf = MockUploadedFile("empty.pdf", b"", "application/pdf")
        result = parse_cv(empty_pdf)
        
        self.assertIsNone(result)
        self.assertTrue(any("فارغ" in err for err in self.st_errors))

    @patch("utils.cv_parser.get_gemini_api_key", return_value=None)
    def test_missing_api_key(self, mock_key):
        """الحالة 6: التعامل مع غياب مفتاح GEMINI_API_KEY"""
        fake_pdf = MockUploadedFile("cv.pdf", b"%PDF-1.4 content", "application/pdf")
        result = parse_cv(fake_pdf)
        
        self.assertIsNone(result)
        self.assertTrue(any("GEMINI_API_KEY" in err for err in self.st_errors))

    @patch("utils.cv_parser.get_gemini_api_key", return_value="fake_api_key_123")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_api_failure_handling(self, mock_configure, mock_model_class, mock_key):
        """الحالة 7: التعامل مع أخطاء الـ API من Google (مثل خطأ الشبكة أو الحظر)"""
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = google_exceptions.GoogleAPIError("API Quota Exceeded")
        mock_model_class.return_value = mock_model_instance

        fake_pdf = MockUploadedFile("cv.pdf", b"%PDF-1.4 content", "application/pdf")
        result = parse_cv(fake_pdf)
        
        self.assertIsNone(result)
        self.assertTrue(any("خطأ في الاتصال بـ Gemini API" in err for err in self.st_errors))

    @patch("utils.cv_parser.get_gemini_api_key", return_value="fake_api_key_123")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_malformed_json_handling(self, mock_configure, mock_model_class, mock_key):
        """الحالة 8: التعامل مع حالة استرجاع نص تالف غير متوافق مع JSON"""
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        fake_pdf = MockUploadedFile("cv.pdf", b"%PDF-1.4 content", "application/pdf")
        result = parse_cv(fake_pdf)
        
        self.assertIsNone(result)
        self.assertTrue(any("فشل في قراءة استجابة الـ JSON" in err for err in self.st_errors))


if __name__ == "__main__":
    unittest.main()
