"""
وحدة التكامل مع Supabase (Supabase Client & Auth Operations)
تدعم المصادقة السحابية (Sign In / Sign Up) وتخزين الـ UserProfile في PostgreSQL مع دعم الوضع المحلي والـ Fallback التلقائي.
"""

from datetime import datetime
import os
from typing import Any, Dict, Optional, Tuple
import streamlit as st

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = Any  # type: ignore


def get_supabase_credentials() -> Tuple[Optional[str], Optional[str]]:
    """استرجاع رابط ومفتاح Supabase من st.secrets أو متغيرات البيئة."""
    url = None
    key = None

    if hasattr(st, "secrets"):
        if "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
        if "SUPABASE_KEY" in st.secrets:
            key = st.secrets["SUPABASE_KEY"]

    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY")

    return url, key


def is_supabase_configured() -> bool:
    """التحقق مما إذا كانت إعدادات Supabase متوفرة وحزمة supabase مثبتة."""
    if not SUPABASE_AVAILABLE:
        return False
    url, key = get_supabase_credentials()
    return bool(url and key and url.startswith("http") and len(key) > 10)


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Optional[Any]:
    """
    إنشاء عميل Supabase Client ومشاركته بأمان عبر الجلسات.
    يرجع None في حالة عدم وجود الإعدادات لتفعيل وضع الـ Guest تلقائياً.
    """
    if not is_supabase_configured():
        return None

    url, key = get_supabase_credentials()
    try:
        client: Client = create_client(url, key)
        return client
    except Exception as e:
        # تسجيل الخطأ بهدوء وعدم إيقاف التطبيق
        return None


def sign_up_user(email: str, password: str) -> Tuple[bool, str]:
    """
    تسجيل حساب مستخدم جديد في Supabase Auth.
    المخرجات: (نجاح: bool, رسالة توضيحية: str)
    """
    client = get_supabase_client()
    if not client:
        return False, "خدمة التخزين السحابي غير مفعلة حالياً (وضع الزائر نشط)."

    if not email or "@" not in email:
        return False, "يرجى إدخال بريد إلكتروني صحيح."
    if not password or len(password) < 6:
        return False, "يجب أن تتكون كلمة المرور من 6 أحرف على الأقل."

    try:
        res = client.auth.sign_up({
            "email": email.strip(),
            "password": password
        })
        if res.user:
            return True, "تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول وحفظ سيرتك الذاتية."
        return False, "تعذر إنشاء الحساب، يرجى مراجعة البيانات."
    except Exception as e:
        err_msg = str(e)
        if "User already registered" in err_msg:
            return False, "هذا البريد الإلكتروني مسجل مسبقاً، يرجى تسجيل الدخول."
        return False, f"فشل إنشاء الحساب: {err_msg}"


def sign_in_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    تسجيل دخول مستخدم حالي في Supabase Auth.
    المخرجات: (نجاح: bool, رسالة: str, بيانات المستخدم: Optional[dict])
    """
    client = get_supabase_client()
    if not client:
        return False, "خدمة التخزين السحابي غير مفعلة حالياً.", None

    if not email or not password:
        return False, "يرجى إدخال البريد الإلكتروني وكلمة المرور.", None

    try:
        res = client.auth.sign_in_with_password({
            "email": email.strip(),
            "password": password
        })
        if res.user and res.session:
            user_data = {
                "id": str(res.user.id),
                "email": res.user.email,
                "access_token": res.session.access_token
            }
            return True, "تم تسجيل الدخول بنجاح!", user_data
        return False, "بيانات الدخول غير صحيحة.", None
    except Exception as e:
        err_msg = str(e)
        if "Invalid login credentials" in err_msg:
            return False, "البريد الإلكتروني أو كلمة المرور غير صحيحة.", None
        return False, f"خطأ أثناء تسجيل الدخول: {err_msg}", None


def sign_out_user() -> None:
    """تسجيل خروج المستخدم ومسح الجلسة."""
    client = get_supabase_client()
    if client:
        try:
            client.auth.sign_out()
        except Exception:
            pass


def save_profile_to_db(user_id: str, profile_data: Dict[str, Any], email: Optional[str] = None) -> bool:
    """
    حفظ/تحديث (Upsert) السيرة الذاتية للمستخدم في قاعدة بيانات Supabase.
    """
    client = get_supabase_client()
    if not client or not user_id:
        return False

    try:
        payload = {
            "id": user_id,
            "email": email,
            "profile_data": profile_data,
            "updated_at": datetime.utcnow().isoformat()
        }
        res = client.table("user_profiles").upsert(payload).execute()
        return bool(res.data)
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الحفظ السحابي: {str(e)}")
        return False


def load_profile_from_db(user_id: str) -> Optional[Dict[str, Any]]:
    """
    استرجاع السيرة الذاتية المحفوظة للمستخدم من قاعدة بيانات Supabase.
    """
    client = get_supabase_client()
    if not client or not user_id:
        return None

    try:
        res = client.table("user_profiles").select("profile_data").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            profile_json = res.data[0].get("profile_data", None)
            if profile_json and isinstance(profile_json, dict):
                return profile_json
        return None
    except Exception as e:
        st.warning(f"⚠️ تعذر استرجاع السيرة الذاتية السحابية: {str(e)}")
        return None
