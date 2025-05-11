#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天相关路由
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.api.deps import get_current_active_user
from app.modules.auth.models.user import User
from app.modules.chat import crud
from app.modules.chat.schemas.conversation import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    Message,
    MessageCreate,
)

router = APIRouter()


@router.post("/conversations", response_model=Conversation)
def create_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新对话
    """
    conversation = crud.conversation.create_with_owner(
        db=db, obj_in=conversation_in, owner_id=current_user.id
    )
    return conversation


@router.get("/conversations", response_model=List[Conversation])
def read_conversations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前用户的所有对话
    """
    conversations = crud.conversation.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return conversations


@router.get("/conversations/{conversation_id}", response_model=Conversation)
def read_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定对话
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在",
        )
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    return conversation


@router.put("/conversations/{conversation_id}", response_model=Conversation)
def update_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_id: int,
    conversation_in: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新对话
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在",
        )
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    conversation = crud.conversation.update(
        db=db, db_obj=conversation, obj_in=conversation_in
    )
    return conversation


@router.delete("/conversations/{conversation_id}", response_model=Conversation)
def delete_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除对话
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在",
        )
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    conversation = crud.conversation.remove(db=db, id=conversation_id)
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=Message)
def create_message(
    *,
    db: Session = Depends(get_db),
    conversation_id: int,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新消息
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在",
        )
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    message = crud.message.create_with_conversation(
        db=db, obj_in=message_in, conversation_id=conversation_id
    )
    return message


@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
def read_messages(
    *,
    db: Session = Depends(get_db),
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取对话中的所有消息
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在",
        )
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    messages = crud.message.get_multi_by_conversation(
        db=db, conversation_id=conversation_id, skip=skip, limit=limit
    )
    return messages
