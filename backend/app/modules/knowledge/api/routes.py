#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库相关路由
"""
from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.api.deps import get_current_active_user
from app.modules.auth.models.user import User
from app.modules.knowledge import crud
from app.modules.knowledge.schemas.knowledge_base import (
    Document,
    DocumentCreate,
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)

router = APIRouter()


@router.post("/knowledge-bases", response_model=KnowledgeBase)
def create_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_in: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新知识库
    """
    knowledge_base = crud.knowledge_base.create_with_owner(
        db=db, obj_in=knowledge_base_in, owner_id=current_user.id
    )
    return knowledge_base


@router.get("/knowledge-bases", response_model=List[KnowledgeBase])
def read_knowledge_bases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前用户的所有知识库
    """
    knowledge_bases = crud.knowledge_base.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return knowledge_bases


@router.get("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBase)
def read_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定知识库
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    return knowledge_base


@router.put("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBase)
def update_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    knowledge_base_in: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新知识库
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    knowledge_base = crud.knowledge_base.update(
        db=db, db_obj=knowledge_base, obj_in=knowledge_base_in
    )
    return knowledge_base


@router.delete("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBase)
def delete_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除知识库
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    knowledge_base = crud.knowledge_base.remove(db=db, id=knowledge_base_id)
    return knowledge_base


@router.post("/knowledge-bases/{knowledge_base_id}/documents", response_model=Document)
def create_document(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新文档
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    document = crud.document.create_with_knowledge_base(
        db=db, obj_in=document_in, knowledge_base_id=knowledge_base_id
    )
    return document


@router.get("/knowledge-bases/{knowledge_base_id}/documents", response_model=List[Document])
def read_documents(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取知识库中的所有文档
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    documents = crud.document.get_multi_by_knowledge_base(
        db=db, knowledge_base_id=knowledge_base_id, skip=skip, limit=limit
    )
    return documents
