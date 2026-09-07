"""
نماذج البيانات الهيكلية (Pydantic v2 Models) لمنصة CareerHub AI
تضمن صحة البيانات وتوحيد الأنواع للـ ATS والمطابقة الذكية.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class Experience(BaseModel):
    """نموذج الخبرة المهنية."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    company: Optional[str] = None
    title: Optional[str] = None
    period: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class Education(BaseModel):
    """نموذج المؤهل التعليمي."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    university: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    year: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class Project(BaseModel):
    """نموذج المشروع التقني."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    description: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class UserProfile(BaseModel):
    """
    النموذج الرئيسي لبيانات المرشح وسيرته الذاتية.
    متوافق تماماً مع Pydantic v2 ويدعم التحويل التبادلي للـ Dict و JSON.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    full_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """تحويل الكائن إلى Dictionary قياسي نقي."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """تحويل الكائن إلى نص JSON منظم."""
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "UserProfile":
        """إنشاء كائن UserProfile من Dictionary بشكل آمن."""
        if not data:
            return cls()
        return cls.model_validate(data)

    def get(self, key: str, default: Any = None) -> Any:
        """دعم الوصول بأسلوب get() لضمان التوافقية مع القوالب السابقة."""
        val = getattr(self, key, default)
        if val is None:
            return default
        return val

    def __getitem__(self, key: str) -> Any:
        """دعم الوصول بالـ Indexing مثل profile['skills']."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)
