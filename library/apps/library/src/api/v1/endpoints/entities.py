"""
Entity CRUD endpoints for Library Service.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID
import logging

from ....db.database import get_db
from ....db.models import Entity as EntityModel
from ....schemas.entity import (
    EntityCreate, EntityUpdate, EntityResponse, EntityList, EntityFilter
)
from ....messaging import publisher, EventType, Subjects
from ....services.dependency_service import DependencyService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/entities", tags=["Entities"])


# ==================== LIST ENTITIES ====================

@router.get("", response_model=EntityList)
async def list_entities(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by entity type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    health_status: Optional[str] = Query(None, description="Filter by health status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: Session = Depends(get_db)
) -> EntityList:
    """
    List entities with pagination and filtering.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **type**: Filter by entity type (strategy, pipeline, model, etc.)
    - **category**: Filter by category
    - **status**: Filter by status (registered, deployed, active, etc.)
    - **health_status**: Filter by health (healthy, degraded, unhealthy, unknown)
    - **search**: Search text in name and description
    - **tags**: Filter by tags (returns entities with ANY of the tags)
    """
    try:
        # Build query
        query = db.query(EntityModel).filter(EntityModel.deleted_at.is_(None))

        # Apply filters
        if type:
            query = query.filter(EntityModel.type == type)

        if category:
            query = query.filter(EntityModel.category == category)

        if status:
            query = query.filter(EntityModel.status == status)

        if health_status:
            query = query.filter(EntityModel.health_status == health_status)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    EntityModel.name.ilike(search_pattern),
                    EntityModel.description.ilike(search_pattern)
                )
            )

        if tags:
            # Filter entities that have ANY of the specified tags
            query = query.filter(EntityModel.tags.overlap(tags))

        # Get total count (before pagination)
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        entities = query.order_by(EntityModel.created_at.desc()) \
                       .offset(offset) \
                       .limit(page_size) \
                       .all()

        return EntityList(
            entities=[EntityResponse.model_validate(e) for e in entities],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list entities: {str(e)}"
        )


# ==================== GET ENTITY ====================

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: UUID,
    db: Session = Depends(get_db)
) -> EntityResponse:
    """
    Get a single entity by ID.

    Returns 404 if entity not found or deleted.
    """
    try:
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )

        return EntityResponse.model_validate(entity)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity: {str(e)}"
        )


# ==================== CREATE ENTITY ====================

@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreate,
    db: Session = Depends(get_db)
) -> EntityResponse:
    """
    Create a new entity.

    - Validates uniqueness of name
    - Publishes entity.registered event to NATS
    - Returns created entity with ID
    """
    try:
        # Check if entity with same name exists
        existing = db.query(EntityModel).filter(
            EntityModel.name == entity_data.name,
            EntityModel.deleted_at.is_(None)
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entity with name '{entity_data.name}' already exists"
            )

        # Create entity
        entity = EntityModel(**entity_data.model_dump())
        db.add(entity)
        db.commit()
        db.refresh(entity)

        # Sync dependencies if requirements provided
        if entity.requirements:
            DependencyService.sync_dependencies(entity, db)
            db.commit()

        logger.info(f"Created entity: {entity.name} ({entity.entity_id})")

        # Publish NATS event
        try:
            await publisher.publish_entity_registered(
                entity_id=str(entity.entity_id),
                entity_name=entity.name,
                entity_type=entity.type,
                version=entity.version,
                metadata={
                    "category": entity.category,
                    "author": entity.author,
                    "created_by": entity.created_by
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish entity.registered event: {e}")
            # Don't fail the request if NATS publish fails (graceful degradation)

        return EntityResponse.model_validate(entity)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entity: {str(e)}"
        )


# ==================== UPDATE ENTITY ====================

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: UUID,
    entity_data: EntityUpdate,
    db: Session = Depends(get_db)
) -> EntityResponse:
    """
    Update an existing entity.

    - Only provided fields are updated
    - Publishes entity.updated event to NATS
    - Returns updated entity
    """
    try:
        # Get entity
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )

        # Check name uniqueness if name is being updated
        if entity_data.name and entity_data.name != entity.name:
            existing = db.query(EntityModel).filter(
                EntityModel.name == entity_data.name,
                EntityModel.deleted_at.is_(None),
                EntityModel.entity_id != entity_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Entity with name '{entity_data.name}' already exists"
                )

        # Update fields (only those provided)
        update_data = entity_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)

        db.commit()
        db.refresh(entity)

        # Sync dependencies if requirements were updated
        if 'requirements' in update_data:
            DependencyService.sync_dependencies(entity, db)
            db.commit()

        logger.info(f"Updated entity: {entity.name} ({entity.entity_id})")

        # Publish NATS event
        try:
            await publisher.publish_generic_event(
                event_type=EventType.ENTITY_UPDATED,
                subject=Subjects.ENTITY_UPDATED,
                data={
                    "entity_id": str(entity.entity_id),
                    "entity_name": entity.name,
                    "updated_fields": list(update_data.keys())
                },
                entity_id=str(entity.entity_id)
            )
        except Exception as e:
            logger.error(f"Failed to publish entity.updated event: {e}")

        return EntityResponse.model_validate(entity)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update entity: {str(e)}"
        )


# ==================== DELETE ENTITY ====================

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: UUID,
    deleted_by: Optional[str] = Query(None, description="User performing deletion"),
    db: Session = Depends(get_db)
) -> None:
    """
    Soft delete an entity.

    - Sets deleted_at timestamp (soft delete)
    - Publishes entity.deleted event to NATS
    - Returns 204 No Content on success
    """
    try:
        # Get entity
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )

        # Soft delete
        from datetime import datetime
        entity.deleted_at = datetime.utcnow()
        entity.deleted_by = deleted_by

        db.commit()

        logger.info(f"Deleted entity: {entity.name} ({entity.entity_id})")

        # Publish NATS event
        try:
            await publisher.publish_generic_event(
                event_type=EventType.ENTITY_DELETED,
                subject=Subjects.ENTITY_DELETED,
                data={
                    "entity_id": str(entity.entity_id),
                    "entity_name": entity.name,
                    "deleted_by": deleted_by
                },
                entity_id=str(entity.entity_id)
            )
        except Exception as e:
            logger.error(f"Failed to publish entity.deleted event: {e}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity {entity_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entity: {str(e)}"
        )


# ==================== SEARCH ENTITIES ====================

@router.get("/search/", response_model=EntityList)
async def search_entities(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> EntityList:
    """
    Full-text search across entity names and descriptions.

    Uses PostgreSQL ILIKE for case-insensitive search.
    """
    try:
        search_pattern = f"%{q}%"

        query = db.query(EntityModel).filter(
            EntityModel.deleted_at.is_(None),
            or_(
                EntityModel.name.ilike(search_pattern),
                EntityModel.description.ilike(search_pattern),
                EntityModel.tags.any(q)  # Search in tags
            )
        )

        total = query.count()

        offset = (page - 1) * page_size
        entities = query.order_by(EntityModel.created_at.desc()) \
                       .offset(offset) \
                       .limit(page_size) \
                       .all()

        return EntityList(
            entities=[EntityResponse.model_validate(e) for e in entities],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# ==================== GET ENTITY DEPENDENCIES ====================

@router.get("/{entity_id}/dependencies", response_model=List[dict])
async def get_entity_dependencies(
    entity_id: UUID,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get all dependencies for an entity.

    Returns list of entities that this entity depends on.
    """
    try:
        from ....db.models import Dependency

        # Check entity exists
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )

        # Get dependencies
        dependencies = db.query(Dependency).filter(
            Dependency.entity_id == entity_id,
            Dependency.status == 'active'
        ).all()

        result = []
        for dep in dependencies:
            dep_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == dep.depends_on_entity_id
            ).first()

            if dep_entity:
                result.append({
                    "dependency_id": str(dep.dependency_id),
                    "entity": EntityResponse.model_validate(dep_entity).model_dump(),
                    "dependency_type": dep.dependency_type,
                    "min_version": dep.min_version,
                    "max_version": dep.max_version
                })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dependencies for {entity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dependencies: {str(e)}"
        )
