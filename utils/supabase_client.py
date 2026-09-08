"""
وحدة التكامل مع Supabase (Supabase Client & Auth Operations)
تدعم المصادقة السحابية (Sign In / Sign Up) وتخزين الـ UserProfile في PostgreSQL مع دعم الوضع المحلي والـ Fallback التلقائي.
"""

from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import streamlit as st

# محاولة قراءة TOML المباشرة من القرص في حالة عدم تحديث st.secrets في الذاكرة
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


SUPABASE_IMPORT_ERROR: Optional[str] = None

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except Exception as e:
    SUPABASE_AVAILABLE = False
    SUPABASE_IMPORT_ERROR = str(e)
    Client = Any  # type: ignore


def check_supabase_import() -> Tuple[bool, Optional[str]]:
    """محاولة استيراد مكتبة supabase ديناميكياً."""
    global SUPABASE_AVAILABLE, SUPABASE_IMPORT_ERROR
    if not SUPABASE_AVAILABLE:
        try:
            from supabase import create_client, Client
            SUPABASE_AVAILABLE = True
            SUPABASE_IMPORT_ERROR = None
        except Exception as e:
            SUPABASE_AVAILABLE = False
            SUPABASE_IMPORT_ERROR = str(e)
    return SUPABASE_AVAILABLE, SUPABASE_IMPORT_ERROR


def get_supabase_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    استرجاع رابط ومفتاح Supabase:
    1. من st.secrets
    2. مباشرة من ملف .streamlit/secrets.toml
    3. من متغيرات البيئة (os.environ)
    """
    url = None
    key = None

    # 1. من st.secrets
    try:
        if hasattr(st, "secrets"):
            url = st.secrets.get("SUPABASE_URL", None)
            key = st.secrets.get("SUPABASE_KEY", None)
    except Exception:
        pass

    # 2. قراءة مباشرة من القرص كـ Fallback فوري
    if not (url and key):
        secrets_path = Path(".streamlit/secrets.toml")
        if secrets_path.exists():
            try:
                if tomllib is not None:
                    with open(secrets_path, "rb") as f:
                        data = tomllib.load(f)
                        url = url or data.get("SUPABASE_URL")
                        key = key or data.get("SUPABASE_KEY")
                else:
                    # قراءة نصية بسيطة
                    with open(secrets_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line_s = line.strip()
                            if line_s.startswith("SUPABASE_URL"):
                                url = url or line_s.split("=", 1)[1].strip().strip('"\'')
                            elif line_s.startswith("SUPABASE_KEY"):
                                key = key or line_s.split("=", 1)[1].strip().strip('"\'')
            except Exception:
                pass

    # 3. من متغيرات البيئة
    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY")

    return url, key


def is_supabase_configured() -> bool:
    """التحقق مما إذا كانت إعدادات Supabase متوفرة وحزمة supabase مثبتة بنجاح."""
    available, _ = check_supabase_import()
    if not available:
        return False
    url, key = get_supabase_credentials()
    return bool(url and key and str(url).startswith("http") and len(str(key)) > 20)


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Optional[Any]:
    """
    إنشاء عميل Supabase Client ومشاركته بأمان عبر الجلسات.
    """
    if not is_supabase_configured():
        return None

    url, key = get_supabase_credentials()
    try:
        from supabase import create_client
        client: Client = create_client(str(url), str(key))
        return client
    except Exception as e:
        return None


def sign_up_user(email: str, password: str) -> Tuple[bool, str]:
    """
    تسجيل حساب مستخدم جديد في Supabase Auth.
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
