"""
API Models Package
==================
SQLAlchemy ORM models for the API module.
"""

# Keep backwards compatibility by importing from the models directory
import logging

logger = logging.getLogger(__name__)
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
    CourseCategory,
    DifficultyLevel,
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
    QuestionType,
    QuizDifficulty,
    WordDifficulty,
    WordCategory,
)
from apps.api.models.api import (
    Api,
)

__all__ = [
    "AccountType", "EntryType", "InvoiceStatus", "PaymentMethod", "TaxType",
    "Account", "JournalEntry", "JournalItem", "Invoice", "InvoiceItem", "Payment", "Budget", "BudgetAlert", "TaxRate", "FixedAsset",
    "AgricultureSchool", "SchoolField",
    "Course", "Lesson", "Enrollment", "CourseCategory", "DifficultyLevel",
    "LibraryResource",
    "Post", "Comment", "Like",
    "VocabularyWord", "Quiz", "QuizQuestion", "QuizAttempt",
    "QuestionType", "QuizDifficulty", "WordDifficulty", "WordCategory",
    "Api",
]
