"""
محرك استخراج بيانات السيرة الذاتية (CV Parser Engine) باستخدام Gemini API
"""

import json
import os
from typing import Any, Dict, Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import streamlit as st

# أقصى حجم مسموح به للملف (10 ميجابايت)
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# الموديل المستقر المعتمد
DEFAULT_MODEL = "gemini-1.5-flash"

CV_EXTRACTION_PROMPT = """أنت خبير في تحليل وتدقيق السير الذاتية (Technical Recruiter & ATS Expert). 
استخرج المعلومات من السيرة الذاتية المرفقة بدقة بالغة.

القواعد الإلزامية:
1. لو معلومة غير موجودة في السيرة الذاتية، اكتب null — إياك واختراع أي بيانات أو افتراضها.
2. حافظ على اللغة الأصلية للـ CV (عربي أو إنجليزي) — لا تترجم أسماء الشركات، المشاريع، أو الشهادات.
3. الفترات الزمنية بصيغة: "YYYY-MM إلى YYYY-MM" أو "current" لو شغال حالياً.
4. المهارات (skills): مصفوفة نصوص بدون تكرار، أول حرف Capital لكل مهارة بالإنجليزية (مثل: Python, Docker, React).
5. الناتج JSON صريح مطابق للمخطط تماماً بدون أي علامات Markdown أو نصوص خارج نطاق الـ JSON.

المخطط المطلوب (JSON Schema):
{
  "full_name": null,
  "headline": null,
  "summary": null,
  "skills": [],
  "experiences": [
    {
      "company": null,
      "title": null,
      "period": null,
      "achievements": []
    }
  ],
  "education": [
    {
      "university": null,
      "degree": null,
      "field": null,
      "year": null
    }
  ],
  "projects": [
    {
      "name": null,
      "technologies": [],
      "description": null
    }
  ]
}
حلل السيرة الذاتية المرفقة الآن."""


def get_gemini_api_key() -> Optional[str]:
    """استرجاع مفتاح Gemini من st.secrets أو من متغيرات البيئة."""
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY")


def parse_cv(
    uploaded_file, model_name: str = DEFAULT_MODEL
) -> Optional[Dict[str, Any]]:
    """
    استخراج بيانات السيرة الذاتية وإرجاعها كـ Dictionary بايثون جاهز.

    المعاملات:
        uploaded_file: كائن الملف المرفوع من st.file_uploader.
        model_name: اسم نموذج Gemini (الافتراضي: gemini-1.5-flash).
    المخرجات:
        dict: البيانات المستخرجة عند النجاح، أو None في حالة الفشل.
    """
    if uploaded_file is None:
        st.error("❌ لم يتم تحديد أو رفع أي ملف.")
        return None

    filename = getattr(uploaded_file, "name", "").lower()
    file_type = getattr(uploaded_file, "type", "")
    if not (filename.endswith(".pdf") or file_type == "application/pdf"):
        st.error(
            f"❌ نوع الملف غير مدعوم: `{filename}`. يُرجى رفع ملف بصيغة PDF فقط."
        )
        return None

    try:
        if hasattr(uploaded_file, "getvalue"):
            pdf_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            pdf_bytes = uploaded_file.read()
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
        else:
            st.error("❌ تعذر قراءة محتوى الملف المرفوع.")
            return None
    except Exception as read_err:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف: {str(read_err)}")
        return None

    file_size = getattr(uploaded_file, "size", len(pdf_bytes))
    if file_size == 0 or len(pdf_bytes) == 0:
        st.error(
            "❌ الملف المرفوع فارغ (0 بايت). يُرجى رفع سيرة ذاتية صالحة."
        )
        return None

    if file_size > MAX_FILE_SIZE_BYTES:
        current_size_mb = file_size / (1024 * 1024)
        st.error(
            f"❌ حجم الملف ({current_size_mb:.2f} MB) يتجاوز الحد المسموح به ({MAX_FILE_SIZE_MB} MB)."
        )
        return None

    api_key = get_gemini_api_key()
    if not api_key:
        st.error(
            "❌ مفتاح `GEMINI_API_KEY` غير معرّف في `st.secrets` أو متغيرات البيئة."
        )
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)

        response = model.generate_content(
            contents=[
                CV_EXTRACTION_PROMPT,
                {"mime_type": "application/pdf", "data": pdf_bytes},
            ],
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )

        parsed_dict = json.loads(response.text)

        if not isinstance(parsed_dict, dict):
            st.error("❌ استجابة النموذج لم تكن كائناً هيكلياً صالحاً.")
            return None

        return parsed_dict

    except google_exceptions.GoogleAPIError as api_err:
        st.error(
            f"❌ خطأ في الاتصال بـ Gemini API: {str(api_err)}\n"
            "💡 تأكد من صحة المفتاح، والكوتا المتاحة، والاتصال بالإنترنت."
        )
        return None
    except json.JSONDecodeError as json_err:
        st.error(f"❌ فشل في قراءة استجابة الـ JSON: {str(json_err)}")
        return None
    except Exception as general_err:
        st.error(f"❌ حدث خطأ غير متوقع: {str(general_err)}")
        return None
