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
from apps.api.models.api import (
    Api,
)
from apps.api.models.community import (
    Comment,
    Like,
    Post,
)
from apps.api.models.education import (
    Course,
    CourseCategory,
    DifficultyLevel,
    Enrollment,
    Lesson,
)
from apps.api.models.games import (
    QuestionType,
    Quiz,
    QuizAttempt,
    QuizDifficulty,
    QuizQuestion,
    VocabularyWord,
    WordCategory,
    WordDifficulty,
)
from apps.api.models.library import (
    LibraryResource,
)

__all__ = [
    "Account",
    "AccountType",
    "AgricultureSchool",
    "Api",
    "Budget",
    "BudgetAlert",
    "Comment",
    "Course",
    "CourseCategory",
    "DifficultyLevel",
    "Enrollment",
    "EntryType",
    "FixedAsset",
    "Invoice",
    "InvoiceItem",
    "InvoiceStatus",
    "JournalEntry",
    "JournalItem",
    "Lesson",
    "LibraryResource",
    "Like",
    "Payment",
    "PaymentMethod",
    "Post",
    "QuestionType",
    "Quiz",
    "QuizAttempt",
    "QuizDifficulty",
    "QuizQuestion",
    "SchoolField",
    "TaxRate",
    "TaxType",
    "VocabularyWord",
    "WordCategory",
    "WordDifficulty",
]
