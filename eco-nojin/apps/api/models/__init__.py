"""
API Models Package
==================
SQLAlchemy ORM models for the API module.
"""

# Keep backwards compatibility by importing from the models directory
import logging

logger = logging.getLogger(__name__)
from apps.api.models.accounting import (
    Account,
    AccountType,
    Budget,
    BudgetAlert,
    EntryType,
    FixedAsset,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    JournalEntry,
    JournalItem,
    Payment,
    PaymentMethod,
    TaxRate,
    TaxType,
)
from apps.api.models.agriculture_school import (
    AgricultureSchool,
    SchoolField,
)
from apps.api.models.community import (
    Comment,
    Like,
    Post,
)
from apps.api.models.education import (
    Course,
    Enrollment,
    Lesson,
)
from apps.api.models.games import (
    Quiz,
    QuizAttempt,
    QuizQuestion,
    VocabularyWord,
)
from apps.api.models.library import (
    LibraryResource,
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
