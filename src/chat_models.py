"""Pydantic models for chat history and admin functionality."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ========== Conversation Models ==========

class ConversationMetadata(BaseModel):
    """Conversation metadata."""
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    title: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    chapters_referenced: List[int] = Field(default_factory=list)
    characters_mentioned: List[str] = Field(default_factory=list)
    is_archived: bool = False


class ConversationCreate(BaseModel):
    """Request to create a new conversation."""
    user_id: str
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response."""
    conversation_id: str
    user_id: str
    metadata: Dict[str, Any]
    message_count: int


class ConversationListResponse(BaseModel):
    """List of conversations."""
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int


# ========== Message Models ==========

class MessageCreate(BaseModel):
    """Request to create a message."""
    conversation_id: str
    user_query: str
    ai_response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    chapter_references: List[int] = Field(default_factory=list)
    verse_references: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    characters_mentioned: List[str] = Field(default_factory=list)


class MessageResponse(BaseModel):
    """Message response."""
    message_id: str
    conversation_id: str
    timestamp: datetime
    user_query: str
    ai_response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    chapter_references: List[int] = Field(default_factory=list)
    verse_references: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    characters_mentioned: List[str] = Field(default_factory=list)
    response_time_ms: Optional[int] = None


class ConversationHistoryResponse(BaseModel):
    """Conversation history with messages."""
    conversation_id: str
    user_id: str
    metadata: Dict[str, Any]
    messages: List[MessageResponse]
    total_messages: int


# ========== User Models ==========

class UserProfile(BaseModel):
    """User profile."""
    user_id: str
    created_at: datetime
    last_active: datetime
    total_conversations: int = 0
    total_messages: int = 0
    favorite_topics: List[str] = Field(default_factory=list)


class UserStats(BaseModel):
    """User statistics."""
    user_id: str
    total_conversations: int
    total_messages: int
    most_asked_topics: List[str]
    favorite_chapters: List[int]
    first_conversation: Optional[datetime] = None
    last_active: datetime


# ========== Admin Models ==========

class AdminLogin(BaseModel):
    """Admin login request."""
    username: str
    password: str


class AdminAuthResponse(BaseModel):
    """Admin authentication response."""
    success: bool
    token: Optional[str] = None
    message: str


class AdminConversationFilter(BaseModel):
    """Filter for admin conversation queries."""
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    topic: Optional[str] = None
    chapter: Optional[int] = None
    limit: int = 100
    offset: int = 0


class AdminAnalytics(BaseModel):
    """Admin analytics response."""
    total_users: int
    total_conversations: int
    total_messages: int
    messages_today: int
    messages_this_week: int
    active_users_today: int
    top_questions: List[Dict[str, Any]]
    popular_chapters: List[Dict[str, Any]]
    popular_topics: List[Dict[str, Any]]
    avg_response_time_ms: float


class AdminSearchRequest(BaseModel):
    """Admin search request."""
    query: str
    search_in: str = "both"  # question, answer, both
    limit: int = 50


class AdminSearchResult(BaseModel):
    """Admin search result."""
    message_id: str
    conversation_id: str
    user_id: str
    timestamp: datetime
    user_query: str
    ai_response: str
    match_type: str  # question, answer, both


# ========== Enhanced Question Request with Session ==========

class QuestionRequestWithSession(BaseModel):
    """Question request with session/conversation context."""
    question: str
    user_id: Optional[str] = "anonymous"
    conversation_id: Optional[str] = None
    include_context: bool = True


class QuestionResponseWithHistory(BaseModel):
    """Question response with conversation tracking."""
    answer: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    message_id: str
    user_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
