"""
Feedback API Routes for Bhagavad Gita Q&A System

Provides endpoints for submitting and retrieving user feedback.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Pydantic Models
class FeedbackSource(BaseModel):
    """Source reference for an answer."""
    page: int
    source: str


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    question: str = Field(..., description="The user's question")
    answer: str = Field(..., description="The answer provided by the system")
    liked: bool = Field(..., description="True for thumbs up, False for thumbs down")
    user_id: str = Field(..., description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    message_id: Optional[str] = Field(None, description="Optional message ID")
    sources: Optional[List[FeedbackSource]] = Field(None, description="Source references")
    feedback_text: Optional[str] = Field(None, description="Optional text feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "who is krishna",
                "answer": "Hare Krishna! Based on the provided context...",
                "liked": True,
                "user_id": "user_1771826776496_95coi0urc",
                "conversation_id": "1IGGr8YUBo8ZxduTRqeX",
                "message_id": "4WmSE7GyegSZM3BMbWOf",
                "sources": [{"page": 58, "source": "11-Bhagavad-gita_As_It_Is.pdf"}],
                "feedback_text": "Very helpful answer!"
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    success: bool
    feedback_id: str
    message: str
    timestamp: str


class FeedbackStatsResponse(BaseModel):
    """Response model for feedback statistics."""
    total_feedback: int
    thumbs_up: int
    thumbs_down: int
    satisfaction_rate: float
    recent_feedback: List[Dict[str, Any]]


def create_feedback_router(feedback_service) -> APIRouter:
    """
    Create and configure the feedback router.
    
    Args:
        feedback_service: Instance of FeedbackService
    
    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/feedback", tags=["feedback"])
    
    @router.post("", response_model=FeedbackResponse)
    async def submit_feedback(feedback: FeedbackRequest, request: Request):
        """
        Submit user feedback for an answer.
        
        This endpoint allows users to provide thumbs up/down feedback
        on answers they receive from the Q&A system.
        """
        try:
            # Extract metadata from request
            metadata = {
                "user_agent": request.headers.get("user-agent"),
                "referer": request.headers.get("referer"),
                "origin": request.headers.get("origin")
            }
            
            # Convert sources to dict if present
            sources_dict = None
            if feedback.sources:
                sources_dict = [source.dict() for source in feedback.sources]
            
            # Save feedback
            feedback_id = feedback_service.save_feedback(
                question=feedback.question,
                answer=feedback.answer,
                liked=feedback.liked,
                user_id=feedback.user_id,
                conversation_id=feedback.conversation_id,
                message_id=feedback.message_id,
                sources=sources_dict,
                feedback_text=feedback.feedback_text,
                metadata=metadata
            )
            
            return FeedbackResponse(
                success=True,
                feedback_id=feedback_id,
                message="Thank you for your feedback!" if feedback.liked else "Thank you for your feedback. We'll work to improve!",
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            print(f"❌ Error submitting feedback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")
    
    @router.get("/stats", response_model=FeedbackStatsResponse)
    async def get_feedback_stats():
        """
        Get aggregated feedback statistics.
        
        Returns overall satisfaction metrics and recent feedback.
        """
        try:
            stats = feedback_service.get_feedback_stats()
            return FeedbackStatsResponse(**stats)
            
        except Exception as e:
            print(f"❌ Error retrieving feedback stats: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")
    
    @router.get("/user/{user_id}")
    async def get_user_feedback(user_id: str, limit: int = 50):
        """
        Get all feedback from a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of results (default: 50)
        """
        try:
            feedback_list = feedback_service.get_user_feedback(user_id, limit)
            return {
                "user_id": user_id,
                "total": len(feedback_list),
                "feedback": feedback_list
            }
            
        except Exception as e:
            print(f"❌ Error retrieving user feedback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve user feedback: {str(e)}")
    
    @router.get("/conversation/{conversation_id}")
    async def get_conversation_feedback(conversation_id: str, limit: int = 50):
        """
        Get all feedback for a specific conversation.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of results (default: 50)
        """
        try:
            feedback_list = feedback_service.get_conversation_feedback(conversation_id, limit)
            return {
                "conversation_id": conversation_id,
                "total": len(feedback_list),
                "feedback": feedback_list
            }
            
        except Exception as e:
            print(f"❌ Error retrieving conversation feedback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation feedback: {str(e)}")
    
    @router.get("/{feedback_id}")
    async def get_feedback(feedback_id: str):
        """
        Get a specific feedback by ID.
        
        Args:
            feedback_id: The feedback document ID
        """
        try:
            feedback = feedback_service.get_feedback(feedback_id)
            if not feedback:
                raise HTTPException(status_code=404, detail="Feedback not found")
            return feedback
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error retrieving feedback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")
    
    return router
