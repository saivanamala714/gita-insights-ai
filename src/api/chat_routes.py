"""API routes for chat functionality."""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from src.chat_models import (
    QuestionRequestWithSession,
    QuestionResponseWithHistory,
    ConversationCreate,
    ConversationResponse,
    ConversationHistoryResponse
)
from src.services.chat_history_manager import chat_history_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreate):
    """Create a new conversation."""
    try:
        conversation_id = chat_history_manager.create_or_get_conversation(
            user_id=request.user_id,
            title=request.title
        )
        
        # Get conversation details
        conversation = chat_history_manager.firestore.get_conversation(
            request.user_id,
            conversation_id
        )
        
        return ConversationResponse(
            conversation_id=conversation_id,
            user_id=request.user_id,
            metadata=conversation,
            message_count=0
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation(
    conversation_id: str,
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get conversation history."""
    try:
        history = chat_history_manager.get_conversation_history(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationHistoryResponse(**history)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    include_archived: bool = False
):
    """Get all conversations for a user."""
    try:
        conversations = chat_history_manager.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset,
            include_archived=include_archived
        )
        
        return {
            "conversations": conversations,
            "total": len(conversations),
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error getting user conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str
):
    """Delete a conversation."""
    try:
        chat_history_manager.delete_conversation(user_id, conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/context")
async def get_conversation_context(
    conversation_id: str,
    user_id: str,
    context_size: int = 10
):
    """Get recent messages for context."""
    try:
        context = chat_history_manager.get_conversation_context(
            user_id=user_id,
            conversation_id=conversation_id,
            context_size=context_size
        )
        
        return {
            "conversation_id": conversation_id,
            "context": context,
            "context_size": len(context)
        }
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics."""
    try:
        stats = chat_history_manager.get_user_stats(user_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="User not found")
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
