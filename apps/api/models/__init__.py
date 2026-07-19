"""
API Models Package
==================
SQLAlchemy ORM models for the API module.
"""

# Keep backwards compatibility by importing from the models directory
from apps.api.models.accounting import (
    AccountType,
    EntryType,
    InvoiceStatus,
    PaymentMethod,
    TaxType,
    Account,
    JournalEntry,
    JournalItem,
    Invoice,
    InvoiceItem,
    Payment,
    Budget,
    BudgetAlert,
    TaxRate,
    FixedAsset,
)
from apps.api.models.agriculture_school import (
    AgricultureSchool,
    SchoolField,
)
from apps.api.models.education import (
    Course,
    Lesson,
    Enrollment,
)
from apps.api.models.library import (
    LibraryResource,
)
from apps.api.models.community import (
    Post,
    Comment,
    Like,
)
from apps.api.models.games import (
    VocabularyWord,
    Quiz,
    QuizQuestion,
    QuizAttempt,
)

__all__ = [
    "AccountType", "EntryType", "InvoiceStatus", "PaymentMethod", "TaxType",
    "Account", "JournalEntry", "JournalItem", "Invoice", "InvoiceItem", "Payment", "Budget", "BudgetAlert", "TaxRate", "FixedAsset",
    "AgricultureSchool", "SchoolField",
    "Course", "Lesson", "Enrollment",
    "LibraryResource",
    "Post", "Comment", "Like",
    "VocabularyWord", "Quiz", "QuizQuestion", "QuizAttempt",
]
