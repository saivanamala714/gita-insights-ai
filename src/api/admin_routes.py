"""API routes for admin functionality."""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import logging
from datetime import datetime
from src.chat_models import (
    AdminLogin,
    AdminAuthResponse,
    AdminConversationFilter,
    AdminAnalytics,
    AdminSearchRequest
)
from src.services.admin_service import admin_service
from src.services.analytics_service import analytics_service
from src.config.admin_config import admin_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    """Verify admin API key from header."""
    if not x_admin_key or not admin_config.verify_api_key(x_admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return True


@router.post("/login", response_model=AdminAuthResponse)
async def admin_login(credentials: AdminLogin):
    """Admin login endpoint."""
    try:
        if admin_config.verify_credentials(credentials.username, credentials.password):
            # In production, generate a JWT token here
            return AdminAuthResponse(
                success=True,
                token=admin_config.ADMIN_API_KEY,  # For now, return API key
                message="Login successful"
            )
        else:
            return AdminAuthResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def get_all_conversations(
    limit: int = 100,
    offset: int = 0,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    topic: Optional[str] = None,
    chapter: Optional[int] = None,
    _: bool = Depends(verify_admin_key)
):
    """Get all conversations with filtering (admin only)."""
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        result = admin_service.get_all_conversations(
            limit=limit,
            offset=offset,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            topic=topic,
            chapter=chapter
        )
        
        return result
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{user_id}/{conversation_id}")
async def get_conversation_details(
    user_id: str,
    conversation_id: str,
    _: bool = Depends(verify_admin_key)
):
    """Get detailed conversation information (admin only)."""
    try:
        details = admin_service.get_conversation_details(user_id, conversation_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_conversations(
    search_request: AdminSearchRequest,
    _: bool = Depends(verify_admin_key)
):
    """Search across all conversations (admin only)."""
    try:
        results = admin_service.search_all_conversations(
            query=search_request.query,
            search_in=search_request.search_in,
            limit=search_request.limit
        )
        
        return {
            "query": search_request.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_all_users(
    limit: int = 100,
    offset: int = 0,
    _: bool = Depends(verify_admin_key)
):
    """Get all users (admin only)."""
    try:
        result = admin_service.get_all_users(limit=limit, offset=offset)
        return result
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    _: bool = Depends(verify_admin_key)
):
    """Get detailed user information (admin only)."""
    try:
        details = admin_service.get_user_details(user_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="User not found")
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    _: bool = Depends(verify_admin_key)
):
    """Delete all user data (admin only, GDPR compliance)."""
    try:
        admin_service.delete_user_data(user_id)
        return {"message": f"All data for user {user_id} has been deleted"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=AdminAnalytics)
async def get_analytics(
    _: bool = Depends(verify_admin_key)
):
    """Get comprehensive analytics (admin only)."""
    try:
        analytics = analytics_service.get_admin_analytics()
        return AdminAnalytics(**analytics)
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    _: bool = Depends(verify_admin_key)
):
    """Get analytics for a specific user (admin only)."""
    try:
        analytics = analytics_service.get_user_analytics(user_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="User not found")
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def admin_health_check(
    _: bool = Depends(verify_admin_key)
):
    """System health check (admin only)."""
    try:
        health = admin_service.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/update-daily")
async def update_daily_stats(
    _: bool = Depends(verify_admin_key)
):
    """Manually trigger daily stats update (admin only)."""
    try:
        analytics_service.update_daily_stats()
        return {"message": "Daily stats updated successfully"}
    except Exception as e:
        logger.error(f"Error updating daily stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/update-global")
async def update_global_stats(
    _: bool = Depends(verify_admin_key)
):
    """Manually trigger global stats update (admin only)."""
    try:
        analytics_service.update_global_stats()
        return {"message": "Global stats updated successfully"}
    except Exception as e:
        logger.error(f"Error updating global stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/conversation/{user_id}/{conversation_id}")
async def export_conversation(
    user_id: str,
    conversation_id: str,
    format: str = "json",
    _: bool = Depends(verify_admin_key)
):
    """Export a conversation (admin only)."""
    try:
        data = admin_service.export_conversation(user_id, conversation_id, format)
        
        if not data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
