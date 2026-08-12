import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MODERATOR = "MODERATOR"
    SUPPORT = "SUPPORT"
    PREMIUM_USER = "PREMIUM_USER"
    FREE_USER = "FREE_USER"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class SubscriptionStatus(str, enum.Enum):
    FREE = "FREE"
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    INCOMPLETE = "INCOMPLETE"
    INCOMPLETE_EXPIRED = "INCOMPLETE_EXPIRED"
    PENDING = "PENDING"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAID = "PAID"
    UNCOLLECTIBLE = "UNCOLLECTIBLE"
    VOID = "VOID"


class VideoStatus(str, enum.Enum):
    IDEA = "Idea"
    SCRIPTING = "Scripting"
    FILMING = "Filming"
    EDITING = "Editing"
    SCHEDULED = "Scheduled"
    PUBLISHED = "Published"


class NotificationType(str, enum.Enum):
    MILESTONE = "milestone"
    ALERT = "alert"
    AI = "ai"
    SYSTEM = "system"


class NotificationStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    ARCHIVED = "ARCHIVED"


class AIProvider(str, enum.Enum):
    GEMINI = "GEMINI"
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"
    OPENAI_COMPATIBLE = "OPENAI_COMPATIBLE"
    CLAUDE = "CLAUDE"
    MOCK = "MOCK"


class AIRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ReportStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
