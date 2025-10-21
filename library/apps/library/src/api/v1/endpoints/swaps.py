"""
Swap endpoints for Library Service - Hotswap Engine.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

from ....db.database import get_db
from ....db.models import Entity as EntityModel, Swap as SwapModel
from ....schemas.swap import (
    SwapCreate, SwapResponse, SwapList, SwapRollbackRequest, SwapValidation, SwapStatus
)
from ....services.swap_service import SwapService
from ....messaging import publisher, EventType, Subjects

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/swaps", tags=["Swaps"])


# ==================== LIST SWAPS ====================

@router.get("", response_model=SwapList)
async def list_swaps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    status: Optional[str] = Query(None, description="Filter by status"),
    swap_type: Optional[str] = Query(None, description="Filter by swap type"),
    db: Session = Depends(get_db)
) -> SwapList:
    """
    List swaps with pagination and filtering.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **environment**: Filter by environment
    - **status**: Filter by status (pending, in_progress, completed, failed, rolled_back)
    - **swap_type**: Filter by swap type (manual, scheduled, automatic, emergency, rollback)
    """
    try:
        query = db.query(SwapModel)

        if environment:
            query = query.filter(SwapModel.environment == environment)

        if status:
            query = query.filter(SwapModel.status == status)

        if swap_type:
            query = query.filter(SwapModel.swap_type == swap_type)

        total = query.count()

        offset = (page - 1) * page_size
        swaps = query.order_by(SwapModel.initiated_at.desc()) \
                    .offset(offset) \
                    .limit(page_size) \
                    .all()

        return SwapList(
            swaps=[SwapResponse.model_validate(s) for s in swaps],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing swaps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list swaps: {str(e)}"
        )


# ==================== GET SWAP ====================

@router.get("/{swap_id}", response_model=SwapResponse)
async def get_swap(
    swap_id: UUID,
    db: Session = Depends(get_db)
) -> SwapResponse:
    """
    Get a single swap by ID.

    Returns 404 if swap not found.
    """
    try:
        swap = db.query(SwapModel).filter(
            SwapModel.swap_id == swap_id
        ).first()

        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Swap {swap_id} not found"
            )

        return SwapResponse.model_validate(swap)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swap {swap_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get swap: {str(e)}"
        )


# ==================== CREATE SWAP ====================

@router.post("", response_model=SwapResponse, status_code=status.HTTP_201_CREATED)
async def create_swap(
    swap_data: SwapCreate,
    db: Session = Depends(get_db)
) -> SwapResponse:
    """
    Create and execute a swap (or validate if dry_run=True).

    Process:
    1. Validate swap compatibility
    2. If dry_run=True, return validation results without executing
    3. Check for concurrent swaps in environment
    4. Create swap record
    5. Execute swap (deactivate old, activate new)
    6. Publish NATS event
    7. Return swap result

    **Swap Types:**
    - manual: User-initiated swap
    - scheduled: Scheduled swap (e.g., cron)
    - automatic: Auto-triggered by system conditions
    - emergency: Emergency hotfix swap
    - rollback: Rollback to previous version

    **Validation Checks:**
    - Both entities exist and not deleted
    - Entity types match (strategy->strategy, pipeline->pipeline)
    - From entity has active deployment in target environment
    - To entity is ready for deployment
    - Dependencies are met
    - No circular dependencies
    """
    try:
        # Step 1: Validate swap compatibility
        validation = SwapService.validate_swap_compatibility(
            from_entity_id=swap_data.from_entity_id,
            to_entity_id=swap_data.to_entity_id,
            environment=swap_data.environment,
            db=db
        )

        # If dry_run, return validation results without executing
        if swap_data.dry_run:
            # Create a temporary swap response for validation
            return SwapResponse(
                swap_id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
                from_entity_id=swap_data.from_entity_id,
                to_entity_id=swap_data.to_entity_id,
                environment=swap_data.environment,
                swap_type=swap_data.swap_type,
                status=SwapStatus.PENDING,
                initiated_by=swap_data.initiated_by,
                initiated_at=datetime.utcnow(),
                reason=swap_data.reason,
                validation_results=validation.model_dump(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        # If validation failed, return error
        if not validation.can_proceed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Swap validation failed",
                    "validation": validation.model_dump()
                }
            )

        # Step 2: Check for concurrent swaps
        active_swap = SwapService.get_active_swap_in_environment(
            entity_id=swap_data.from_entity_id,
            environment=swap_data.environment,
            db=db
        )

        if active_swap:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another swap is already in progress in {swap_data.environment}: {active_swap.swap_id}"
            )

        # Step 3: Create swap record
        swap = SwapModel(
            from_entity_id=swap_data.from_entity_id,
            to_entity_id=swap_data.to_entity_id,
            environment=swap_data.environment,
            swap_type=swap_data.swap_type,
            status=SwapStatus.IN_PROGRESS,
            initiated_by=swap_data.initiated_by,
            reason=swap_data.reason,
            validation_results=validation.model_dump()
        )

        db.add(swap)
        db.flush()  # Get swap_id without committing

        logger.info(f"Created swap {swap.swap_id}: {swap_data.from_entity_id} -> {swap_data.to_entity_id}")

        # Step 4: Execute swap
        success, error_msg = SwapService.execute_swap(
            swap=swap,
            config_override=swap_data.config_override,
            parameters_override=swap_data.parameters_override,
            db=db
        )

        if not success:
            db.commit()  # Commit failed swap record
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Swap execution failed: {error_msg}"
            )

        db.commit()
        db.refresh(swap)

        logger.info(
            f"Swap completed: {swap.swap_id} in {swap.environment} "
            f"(downtime: {swap.downtime_milliseconds}ms)"
        )

        # Step 5: Publish NATS event
        try:
            await publisher.publish_generic_event(
                event_type=EventType.ENTITY_UPDATED,  # Could add SWAP_COMPLETED event type
                subject=Subjects.ENTITY_UPDATED,
                data={
                    "swap_id": str(swap.swap_id),
                    "from_entity_id": str(swap.from_entity_id),
                    "to_entity_id": str(swap.to_entity_id),
                    "environment": swap.environment,
                    "swap_type": swap.swap_type,
                    "downtime_ms": swap.downtime_milliseconds,
                    "initiated_by": swap.initiated_by
                },
                entity_id=str(swap.to_entity_id)
            )
        except Exception as e:
            logger.error(f"Failed to publish swap event: {e}")

        return SwapResponse.model_validate(swap)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating swap: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create swap: {str(e)}"
        )


# ==================== ROLLBACK SWAP ====================

@router.post("/{swap_id}/rollback", response_model=SwapResponse)
async def rollback_swap(
    swap_id: UUID,
    rollback_data: SwapRollbackRequest,
    db: Session = Depends(get_db)
) -> SwapResponse:
    """
    Rollback a completed swap.

    Process:
    1. Get swap record
    2. Verify swap is completed (can't rollback failed/pending swaps)
    3. Reactivate from deployment
    4. Deactivate to deployment
    5. Update entity statuses
    6. Update swap record
    7. Publish NATS event

    **Requirements:**
    - Swap must be in 'completed' status
    - Both deployments must still exist
    """
    try:
        # Get swap
        swap = db.query(SwapModel).filter(
            SwapModel.swap_id == swap_id
        ).first()

        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Swap {swap_id} not found"
            )

        # Execute rollback
        success, error_msg = SwapService.rollback_swap(
            swap=swap,
            rolled_back_by=rollback_data.rolled_back_by,
            reason=rollback_data.reason,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        db.commit()
        db.refresh(swap)

        logger.info(f"Swap rolled back: {swap_id} by {rollback_data.rolled_back_by}")

        # Publish NATS event
        try:
            await publisher.publish_generic_event(
                event_type=EventType.ENTITY_UPDATED,
                subject=Subjects.ENTITY_UPDATED,
                data={
                    "swap_id": str(swap.swap_id),
                    "action": "rollback",
                    "from_entity_id": str(swap.from_entity_id),
                    "to_entity_id": str(swap.to_entity_id),
                    "environment": swap.environment,
                    "rolled_back_by": rollback_data.rolled_back_by,
                    "reason": rollback_data.reason
                },
                entity_id=str(swap.from_entity_id)
            )
        except Exception as e:
            logger.error(f"Failed to publish rollback event: {e}")

        return SwapResponse.model_validate(swap)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back swap {swap_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback swap: {str(e)}"
        )


# ==================== GET ENTITY SWAPS ====================

@router.get("/entity/{entity_id}/swaps", response_model=SwapList)
async def get_entity_swaps(
    entity_id: UUID,
    environment: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> SwapList:
    """
    Get all swaps for a specific entity (as either from or to entity).

    - **entity_id**: Entity to get swaps for
    - **environment**: Filter by environment
    - **status**: Filter by status
    """
    try:
        # Verify entity exists
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )

        # Build query - include swaps where entity is either from or to
        query = db.query(SwapModel).filter(
            (SwapModel.from_entity_id == entity_id) | (SwapModel.to_entity_id == entity_id)
        )

        if environment:
            query = query.filter(SwapModel.environment == environment)

        if status:
            query = query.filter(SwapModel.status == status)

        total = query.count()

        offset = (page - 1) * page_size
        swaps = query.order_by(SwapModel.initiated_at.desc()) \
                    .offset(offset) \
                    .limit(page_size) \
                    .all()

        return SwapList(
            swaps=[SwapResponse.model_validate(s) for s in swaps],
            total=total,
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity swaps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity swaps: {str(e)}"
        )
