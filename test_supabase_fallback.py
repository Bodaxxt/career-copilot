"""
اختبارات وحدة للتحقق من تكامل Supabase والتعافي التلقائي لوضع الزائر (Guest Fallback)
"""

import unittest
from unittest.mock import MagicMock, patch
from utils.supabase_client import (
    is_supabase_configured,
    get_supabase_client,
    sign_in_user,
    sign_up_user,
    save_profile_to_db,
    load_profile_from_db,
)


class TestSupabaseGuestFallback(unittest.TestCase):

    @patch("utils.supabase_client.get_supabase_credentials", return_value=(None, None))
    def test_guest_fallback_when_unconfigured(self, mock_creds):
        """التحقق من تفعيل وضع الزائر التلقائي بدون أي انهيار عند غياب المفاتيح:"""
        self.assertFalse(is_supabase_configured())
        self.assertIsNone(get_supabase_client())

        # عمليات المصادقة تعود برسائل واضحة دون أخطاء برمجية
        ok, msg, user = sign_in_user("test@example.com", "pass123")
        self.assertFalse(ok)
        self.assertIsNone(user)

        ok_up, msg_up = sign_up_user("test@example.com", "pass123")
        self.assertFalse(ok_up)

        # عمليات الحفظ والاسترجاع تعود بـ False و None دون انهيار
        self.assertFalse(save_profile_to_db("fake_id", {"skills": ["Python"]}))
        self.assertIsNone(load_profile_from_db("fake_id"))

    @patch("utils.supabase_client.get_supabase_client")
    def test_save_and_load_profile_with_mocked_supabase(self, mock_get_client):
        """التحقق من عمليات الحفظ والاسترجاع عند توفر اتصال Supabase:"""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_upsert.execute.return_value = MagicMock(data=[{"id": "user_123"}])
        mock_table.upsert.return_value = mock_upsert

        # استرجاع
        mock_select = MagicMock()
        mock_eq = MagicMock()
        mock_eq.execute.return_value = MagicMock(data=[{"profile_data": {"full_name": "سارة", "skills": ["Python"]}}])
        mock_select.eq.return_value = mock_eq
        mock_table.select.return_value = mock_select

        mock_client.table.return_value = mock_table
        mock_get_client.return_value = mock_client

        # تجربة الحفظ
        save_result = save_profile_to_db("user_123", {"full_name": "سارة", "skills": ["Python"]})
        self.assertTrue(save_result)

        # تجربة الاسترجاع
        loaded_data = load_profile_from_db("user_123")
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["full_name"], "سارة")


if __name__ == "__main__":
    unittest.main()
