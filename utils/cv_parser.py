"""
محرك استخراج بيانات السيرة الذاتية (CV Parser Engine) باستخدام Gemini API ومكتبة pypdf
يدعم الاستخراج السحابي، والاستخراج النصي المحلي، وآليات التعافي عند حدوث أخطاء (Fallback).
"""

import io
import json
import os
from typing import Any, Dict, Optional, Tuple
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import pypdf
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
حلل السيرة الذاتية الآن."""


def get_gemini_api_key() -> Optional[str]:
    """استرجاع مفتاح Gemini من st.secrets أو من متغيرات البيئة."""
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY")


def extract_raw_text_from_pdf(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    استخراج النص الخام محلياً من ملف PDF باستخدام pypdf.
    
    المعاملات:
        uploaded_file: كائن الملف المرفوع.
        
    المخرجات:
        (raw_text, error_message): النص المستخرج أو رسالة الخطأ إن وجدت.
    """
    try:
        # قراءة البايتات بأمان
        if hasattr(uploaded_file, "getvalue"):
            pdf_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            pdf_bytes = uploaded_file.read()
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
        else:
            return None, "تعذر قراءة محتوى الملف المرفوع."

        if not pdf_bytes or len(pdf_bytes) == 0:
            return None, "الملف المرفوع فارغ (0 بايت)."

        stream = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(stream)

        # التحقق من تشفير الملف أو حمايته بكلمة مرور
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return None, "الملف محمي بكلمة مرور. يرجى رفع نسخة غير مشفرة."

        extracted_text_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_text_pages.append(f"--- [صفحة {i+1}] ---\n{page_text}")

        full_text = "\n\n".join(extracted_text_pages).strip()
        if not full_text:
            return None, "لم يتم العثور على نصوص قابلة للقراءة داخل ملف الـ PDF (قد يكون ملف صور ممسوح ضوئياً)."

        return full_text, None

    except pypdf.errors.PdfReadError as pdf_err:
        return None, f"الملف تالف أو غير صالح كـ PDF: {str(pdf_err)}"
    except Exception as e:
        return None, f"خطأ غير متوقع أثناء استخراج النص محلياً: {str(e)}"


def parse_cv_from_text(
    raw_text: str, model_name: str = DEFAULT_MODEL
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    تحليل واستخراج البيانات الهيكلية من النص الخام للسيرة الذاتية عبر Gemini.
    تُستخدم كـ Fallback عند تعذر إرسال ملف الـ PDF الخام.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return None, "مفتاح GEMINI_API_KEY غير متوفر في st.secrets أو متغيرات البيئة."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)

        combined_prompt = f"{CV_EXTRACTION_PROMPT}\n\nنص السيرة الذاتية للتحليل:\n```text\n{raw_text}\n```"
        response = model.generate_content(
            contents=[combined_prompt],
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )

        parsed_dict = json.loads(response.text)
        if not isinstance(parsed_dict, dict):
            return None, "استجابة النموذج لم تكن كائناً هيكلياً صالحاً."

        return parsed_dict, None

    except google_exceptions.GoogleAPIError as api_err:
        return None, f"خطأ من Gemini API: {str(api_err)}"
    except json.JSONDecodeError as json_err:
        return None, f"فشل في فك ترميز JSON: {str(json_err)}"
    except Exception as err:
        return None, f"خطأ غير متوقع: {str(err)}"


def parse_cv(
    uploaded_file, model_name: str = DEFAULT_MODEL
) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    الدالة الرئيسية لتحليل السيرة الذاتية.
    تقوم بـ:
    1. استخراج النص الخام محلياً (pypdf) لحفظه في الجلسة وللطوارئ.
    2. إرسال ملف الـ PDF مباشرة إلى Gemini 1.5 Flash.
    3. في حالة فشل الـ PDF المباشر، تحاول الإرسال عبر النص المستخرج.

    المخرجات:
        (parsed_dict, raw_text, error_message)
    """
    if uploaded_file is None:
        return None, None, "لم يتم تحديد أو رفع أي ملف."

    filename = getattr(uploaded_file, "name", "").lower()
    file_type = getattr(uploaded_file, "type", "")
    if not (filename.endswith(".pdf") or file_type == "application/pdf"):
        return None, None, f"نوع الملف غير مدعوم: `{filename}`. يُرجى رفع ملف بصيغة PDF فقط."

    try:
        if hasattr(uploaded_file, "getvalue"):
            pdf_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            pdf_bytes = uploaded_file.read()
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
        else:
            return None, None, "تعذر قراءة محتوى الملف المرفوع."
    except Exception as read_err:
        return None, None, f"حدث خطأ أثناء قراءة الملف: {str(read_err)}"

    file_size = getattr(uploaded_file, "size", len(pdf_bytes))
    if file_size == 0 or len(pdf_bytes) == 0:
        return None, None, "الملف المرفوع فارغ (0 بايت). يُرجى رفع سيرة ذاتية صالحة."

    if file_size > MAX_FILE_SIZE_BYTES:
        current_size_mb = file_size / (1024 * 1024)
        return (
            None,
            None,
            f"حجم الملف ({current_size_mb:.2f} MB) يتجاوز الحد الأقصى المسموح به ({MAX_FILE_SIZE_MB} MB).",
        )

    # استخراج النص الخام محلياً كخطوة أولى لضمان سلامة الملف وتوفير نسخة احتياطية
    raw_text, local_text_err = extract_raw_text_from_pdf(uploaded_file)

    api_key = get_gemini_api_key()
    if not api_key:
        return (
            None,
            raw_text,
            "مفتاح `GEMINI_API_KEY` غير معرّف في `st.secrets` أو متغيرات البيئة. يمكنك استخدام التعديل اليدوي للنص المستخرج.",
        )

    # محاولة الاستخراج المباشر عبر الـ PDF Bytes
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
        if isinstance(parsed_dict, dict):
            return parsed_dict, raw_text, None

    except google_exceptions.ResourceExhausted:
        # خطأ تجاوز الكوتا (Rate Limit 429) -> المحاولة عبر النص الخام
        if raw_text:
            text_parsed, text_err = parse_cv_from_text(raw_text, model_name=model_name)
            if text_parsed:
                return text_parsed, raw_text, None
        return (
            None,
            raw_text,
            "⚠️ تم تجاوز حد الطلبات لـ Gemini API (Rate Limit 429 / Quota Exceeded). يمكنك فحص النص المستخرج محلياً وتعبئة البيانات يدوياً.",
        )

    except google_exceptions.GoogleAPIError as api_err:
        # في حالة خطأ عام، نحاول عبر النص الخام إن توفر
        if raw_text:
            text_parsed, _ = parse_cv_from_text(raw_text, model_name=model_name)
            if text_parsed:
                return text_parsed, raw_text, None
        return None, raw_text, f"خطأ في الاتصال بـ Gemini API: {str(api_err)}"

    except json.JSONDecodeError as json_err:
        return None, raw_text, f"استجابة النموذج لم تكن بصيغة JSON سليمة: {str(json_err)}"

    except Exception as general_err:
        return None, raw_text, f"حدث خطأ غير متوقع أثناء معالجة الـ PDF: {str(general_err)}"

    return None, raw_text, "تعذر استخراج البيانات بصورة صحيحة."
