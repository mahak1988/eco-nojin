"""
Database Models for Knowledge Graph Module
مدل‌های پایگاه داده برای ماژول دانش‌یار

این ماژول شامل مدل‌های SQLAlchemy برای:
- مفاهیم و موجودیت‌ها (Concepts/Entities)
- روابط معنایی (Semantic Relationships)
- مستندات و منابع (Documents/Sources)
- برچسب‌ها و دسته‌بندی‌ها (Tags/Categories)
- جستجو و نمایه‌سازی (Search/Indexing)
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Text, Boolean, JSON, Enum as SQLEnum, Table, Index
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class EntityType(str, Enum):
    """انواع موجودیت‌های دانش"""
    CONCEPT = "concept"           # مفهوم انتزاعی
    TERM = "term"                 # اصطلاح تخصصی
    PERSON = "person"             # شخص
    ORGANIZATION = "organization" # سازمان
    LOCATION = "location"         # مکان
    EVENT = "event"               # رویداد
    PROCESS = "process"           # فرآیند
    METHOD = "method"             # روش/متدولوژی
    TOOL = "tool"                 # ابزار
    DATASET = "dataset"           # مجموعه داده
    MODEL = "model"               # مدل
    STANDARD = "standard"         # استاندارد
    POLICY = "policy"             # سیاست/خط‌مشی


class RelationType(str, Enum):
    """انواع روابط معنایی"""
    IS_A = "is_a"                     # رابطه طبقه‌بندی (مثلاً: سیب is_a میوه)
    PART_OF = "part_of"               # رابطه جزء-کل
    HAS_PART = "has_part"             # رابطه کل-جزء
    RELATED_TO = "related_to"         # رابطه عمومی
    CAUSES = "causes"                 # رابطه علت-معلولی
    PREVENTS = "prevents"             # رابطه پیشگیری
    INFLUENCES = "influences"         # رابطه تأثیرگذاری
    MEASURES = "measures"             # رابطه اندازه‌گیری
    USED_BY = "used_by"               # رابطه استفاده
    DEFINES = "defines"               # رابطه تعریف
    IMPLEMENTS = "implements"         # رابطه پیاده‌سازی
    SIMILAR_TO = "similar_to"         # رابطه شباهت
    OPPOSITE_TO = "opposite_to"       # رابطه تضاد
    DERIVED_FROM = "derived_from"     # رابطه اشتقاق
    APPLIES_TO = "applies_to"         # رابطه کاربرد
    LOCATED_IN = "located_in"         # رابطه مکانی
    CREATED_BY = "created_by"         # رابطه خالقیت
    MEMBER_OF = "member_of"           # رابطه عضویت
    PARTICIPATES_IN = "participates_in"  # رابطه مشارکت


class Concept(Base):
    """
    مفهوم یا موجودیت در گراف دانش
    هسته اصلی سیستم دانش‌یار
    """
    __tablename__ = "knowledge_concepts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # اطلاعات پایه
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # نام انگلیسی
    name_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # نام فارسی
    
    # نوع و دسته‌بندی
    entity_type: Mapped[str] = mapped_column(SQLEnum(EntityType), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # توضیحات و تعاریف
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # نمایه‌سازی معنایی
    embeddings: Mapped[Optional[List[float]]] = mapped_column(
        JSON, nullable=True, 
        comment="بردارهای جاسازی شده برای جستجوی معنایی"
    )
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # متادیتا
    synonyms: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    abbreviations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # وضعیت
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    importance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # کاربر ایجادکننده/ویرایشگر
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # روابط
    outgoing_relations: Mapped[List["SemanticRelation"]] = relationship(
        "SemanticRelation",
        foreign_keys="SemanticRelation.source_concept_id",
        back_populates="source_concept",
        cascade="all, delete-orphan"
    )
    incoming_relations: Mapped[List["SemanticRelation"]] = relationship(
        "SemanticRelation",
        foreign_keys="SemanticRelation.target_concept_id",
        back_populates="target_concept"
    )
    
    # مستندات مرتبط
    document_concepts: Mapped[List["DocumentConcept"]] = relationship(
        "DocumentConcept", back_populates="concept", cascade="all, delete-orphan"
    )
    
    # فرزندان (برای سلسله مراتب)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("knowledge_concepts.id"), nullable=True
    )
    children: Mapped[List["Concept"]] = relationship(
        "Concept",
        backref="parent",
        remote_side=[id],
        foreign_keys=[parent_id]
    )
    
    # ایندکس‌ها
    __table_args__ = (
        Index('idx_concept_name_fulltext', 'name'),
        Index('idx_concept_category', 'category'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Concept(id={self.id}, name='{self.name}', type='{self.entity_type}')>"


class SemanticRelation(Base):
    """
    روابط معنایی بین مفاهیم
    تشکیل‌دهنده یال‌های گراف دانش
    """
    __tablename__ = "semantic_relations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # مفاهیم مرتبط
    source_concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_concepts.id"), nullable=False
    )
    target_concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_concepts.id"), nullable=False
    )
    
    # نوع رابطه
    relation_type: Mapped[str] = mapped_column(SQLEnum(RelationType), nullable=False)
    
    # توضیحات رابطه
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # وزن و اطمینان
    weight: Mapped[Optional[float]] = mapped_column(Float, default=1.0)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # منبع استخراج رابطه
    source_type: Mapped[str] = mapped_column(
        SQLEnum("manual", "extracted", "inferred", "imported", name="relation_source"),
        default="manual"
    )
    source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # متادیتا
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # وضعیت
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط ORM
    source_concept: Mapped["Concept"] = relationship(
        "Concept",
        foreign_keys=[source_concept_id],
        back_populates="outgoing_relations"
    )
    target_concept: Mapped["Concept"] = relationship(
        "Concept",
        foreign_keys=[target_concept_id],
        back_populates="incoming_relations"
    )
    
    # ایندکس‌ها
    __table_args__ = (
        Index('idx_relation_source_target', 'source_concept_id', 'target_concept_id'),
        Index('idx_relation_type', 'relation_type'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<SemanticRelation({self.source_concept_id} -[{self.relation_type}]-> {self.target_concept_id})>"


class Document(Base):
    """
    مستندات و منابع دانش
    مقالات، گزارش‌ها، کتاب‌ها و سایر منابع
    """
    __tablename__ = "knowledge_documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # اطلاعات کتابشناختی
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # نوع سند
    doc_type: Mapped[str] = mapped_column(
        SQLEnum(
            "article", "report", "book", "thesis", "standard", 
            "policy", "manual", "dataset", "webpage", "other",
            name="document_type"
        ),
        nullable=False
    )
    
    # محتوا
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # شناسه‌ها
    doi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # نویسندگان/پدیدآورندگان
    authors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # تاریخ انتشار
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # ناشر
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # زبان
    language: Mapped[str] = mapped_column(String(10), default="fa")
    
    # نمایه‌سازی
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    embeddings: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # فایل
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # وضعیت
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    access_level: Mapped[str] = mapped_column(
        SQLEnum("public", "internal", "restricted", "private", name="access_level"),
        default="internal"
    )
    
    # آمار
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # کاربر
    uploaded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    concept_links: Mapped[List["DocumentConcept"]] = relationship(
        "DocumentConcept", back_populates="document", cascade="all, delete-orphan"
    )
    
    # ایندکس‌ها
    __table_args__ = (
        Index('idx_doc_title', 'title'),
        Index('idx_doc_year', 'year'),
        Index('idx_doc_type', 'doc_type'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title[:50]}...', type='{self.doc_type}')>"


class DocumentConcept(Base):
    """
    ارتباط بین مستندات و مفاهیم
    نشان می‌دهد کدام مفاهیم در کدام مستندات مطرح شده‌اند
    """
    __tablename__ = "document_concepts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_documents.id"), nullable=False
    )
    concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_concepts.id"), nullable=False
    )
    
    # نحوه اشاره به مفهوم در سند
    mention_count: Mapped[int] = mapped_column(Integer, default=1)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # بخش‌های سند که مفهوم در آن ذکر شده
    sections: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    page_numbers: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    
    # متن اطراف اشاره
    context_snippets: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    document: Mapped["Document"] = relationship("Document", back_populates="concept_links")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="document_concepts")
    
    __table_args__ = (
        # یکتایی جفت سند-مفهوم
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<DocumentConcept(doc={self.document_id}, concept={self.concept_id})>"


class Tag(Base):
    """
    برچسب‌ها برای دسته‌بندی و سازماندهی مفاهیم و مستندات
    """
    __tablename__ = "knowledge_tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name_fa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # سلسله مراتب تگ‌ها
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("knowledge_tags.id"), nullable=True
    )
    children: Mapped[List["Tag"]] = relationship(
        "Tag",
        backref="parent",
        remote_side=[id]
    )
    
    # تعداد استفاده
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


# جدول ارتباطی مفاهیم و تگ‌ها
concept_tags = Table(
    'concept_tags',
    Base.metadata,
    Column('concept_id', Integer, ForeignKey('knowledge_concepts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('knowledge_tags.id'), primary_key=True)
)


# جدول ارتباطی مستندات و تگ‌ها
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('knowledge_documents.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('knowledge_tags.id'), primary_key=True)
)


class KnowledgeSource(Base):
    """
    منابع خارجی دانش (Ontologyها، پایگاه‌های دانش دیگر)
    برای واردات و همگام‌سازی دانش
    """
    __tablename__ = "knowledge_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(
        SQLEnum("ontology", "database", "api", "file", "web_scrape", name="source_type"),
        nullable=False
    )
    
    # جزئیات اتصال
    connection_string: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # فرمت و پروتکل
    format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # RDF, OWL, JSON-LD, etc.
    protocol: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # زمان‌بندی همگام‌سازی
    sync_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_status: Mapped[str] = mapped_column(
        SQLEnum("pending", "running", "success", "failed", name="sync_status"),
        default="pending"
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # آمار
    concepts_imported: Mapped[int] = mapped_column(Integer, default=0)
    relations_imported: Mapped[int] = mapped_column(Integer, default=0)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<KnowledgeSource(id={self.id}, name='{self.name}', type='{self.source_type}')>"


class SearchLog(Base):
    """
    لاگ جستجوها برای تحلیل رفتار کاربران و بهبود جستجو
    """
    __tablename__ = "search_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # query
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    query_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # نتایج
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_concept_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    clicked_document_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    
    # فیلترها
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # کاربر و جلسه
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # زمان
    search_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # عملکرد
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<SearchLog(id={self.id}, query='{self.query[:50]}...')>"


class OntologyMapping(Base):
    """
    نگاشت بین مفاهیم داخلی و ontologyهای خارجی
    برای یکپارچه‌سازی با استانداردهای بین‌المللی
    """
    __tablename__ = "ontology_mappings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_concepts.id"), nullable=False
    )
    
    # مشخصات مفهوم خارجی
    external_ontology: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., SNOMED-CT, AGROVOC
    external_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    external_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # نوع نگاشت
    mapping_type: Mapped[str] = mapped_column(
        SQLEnum("exact", "broad", "narrow", "related", name="mapping_type"),
        nullable=False
    )
    
    # اطمینان
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    concept: Mapped["Concept"] = relationship("Concept")
    
    def __repr__(self):
        return f"<OntologyMapping(concept={self.concept_id}, ontology='{self.external_ontology}')>"
