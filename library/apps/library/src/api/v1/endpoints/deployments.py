"""
Deployment endpoints for Library Service.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

from ....db.database import get_db
from ....db.models import Entity as EntityModel, Deployment as DeploymentModel
from ....schemas.deployment import (
    DeploymentCreate, DeploymentUpdate, DeploymentResponse,
    DeploymentList, RollbackRequest, DeploymentEnvironment, DeploymentStatus
)
from ....services.deployment_service import DeploymentService
from ....messaging import publisher, EventType, Subjects

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deployments", tags=["Deployments"])


# ==================== LIST DEPLOYMENTS ====================

@router.get("", response_model=DeploymentList)
async def list_deployments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entity_id: Optional[UUID] = Query(None, description="Filter by entity"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> DeploymentList:
    """List deployments with pagination and filtering."""
    try:
        query = db.query(DeploymentModel)

        if entity_id:
            query = query.filter(DeploymentModel.entity_id == entity_id)

        if environment:
            query = query.filter(DeploymentModel.environment == environment)

        if status:
            query = query.filter(DeploymentModel.status == status)

        total = query.count()

        offset = (page - 1) * page_size
        deployments = query.order_by(DeploymentModel.deployed_at.desc()) \
                          .offset(offset) \
                          .limit(page_size) \
                          .all()

        return DeploymentList(
            deployments=[DeploymentResponse.model_validate(d) for d in deployments],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing deployments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== GET DEPLOYMENT ====================

@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID,
    db: Session = Depends(get_db)
) -> DeploymentResponse:
    """Get deployment by ID."""
    deployment = db.query(DeploymentModel).filter(
        DeploymentModel.deployment_id == deployment_id
    ).first()

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found"
        )

    return DeploymentResponse.model_validate(deployment)


# ==================== CREATE DEPLOYMENT ====================

@router.post("", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment_data: DeploymentCreate,
    db: Session = Depends(get_db)
) -> DeploymentResponse:
    """
    Deploy an entity to an environment.

    Process:
    1. Validate entity exists
    2. Run pre-deployment validation
    3. Deactivate existing deployments in environment
    4. Create deployment record
    5. Update entity status
    6. Run post-deployment validation
    7. Publish deployment event
    """
    start_time = datetime.utcnow()

    try:
        # Get entity
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == deployment_data.entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {deployment_data.entity_id} not found"
            )

        # Pre-deployment validation
        validation = DeploymentService.validate_pre_deployment(
            entity, deployment_data.environment, db
        )

        if not validation.passed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Pre-deployment validation failed",
                    "errors": validation.errors,
                    "warnings": validation.warnings
                }
            )

        # Deactivate existing deployments in this environment
        existing_deployments = db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == entity.entity_id,
            DeploymentModel.environment == deployment_data.environment,
            DeploymentModel.status == 'active'
        ).all()

        for existing in existing_deployments:
            existing.status = 'inactive'
            logger.info(f"Deactivated deployment {existing.deployment_id}")

        # Create deployment
        config_snapshot = deployment_data.config_override if deployment_data.config_override else entity.config
        params_snapshot = deployment_data.parameters_override if deployment_data.parameters_override else entity.parameters

        deployment = DeploymentModel(
            entity_id=entity.entity_id,
            version=entity.version,
            environment=deployment_data.environment,
            config_snapshot=config_snapshot,
            parameters_snapshot=params_snapshot,
            status='active',
            deployed_by=deployment_data.deployed_by,
            deployment_method=deployment_data.deployment_method or 'api'
        )

        db.add(deployment)
        db.flush()  # Get deployment_id without committing

        # Update entity
        entity.status = 'deployed'
        entity.deployed_at = datetime.utcnow()
        entity.deployed_by = deployment_data.deployed_by
        entity.deployment_config = config_snapshot

        # Calculate duration
        deployment.deployment_duration_seconds = int(
            (datetime.utcnow() - start_time).total_seconds()
        )

        # Post-deployment validation
        post_validation = DeploymentService.validate_post_deployment(deployment, db)
        deployment.validation_results = post_validation.model_dump()

        db.commit()
        db.refresh(deployment)

        logger.info(
            f"Deployed {entity.name} ({entity.entity_id}) "
            f"to {deployment_data.environment} as {deployment.deployment_id}"
        )

        # Publish NATS event
        try:
            await publisher.publish_deployment_completed(
                entity_id=str(entity.entity_id),
                deployment_id=str(deployment.deployment_id),
                environment=deployment_data.environment,
                version=entity.version,
                metadata={
                    "deployed_by": deployment_data.deployed_by,
                    "duration_seconds": deployment.deployment_duration_seconds
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish deployment event: {e}")

        return DeploymentResponse.model_validate(deployment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating deployment: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== ROLLBACK DEPLOYMENT ====================

@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse)
async def rollback_deployment(
    deployment_id: UUID,
    rollback_data: RollbackRequest,
    db: Session = Depends(get_db)
) -> DeploymentResponse:
    """
    Rollback a deployment.

    Process:
    1. Find current deployment
    2. Find previous deployment (or specified target)
    3. Deactivate current deployment
    4. Reactivate previous deployment
    5. Update entity configuration
    6. Publish rollback event
    """
    try:
        # Get current deployment
        current = db.query(DeploymentModel).filter(
            DeploymentModel.deployment_id == deployment_id
        ).first()

        if not current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment {deployment_id} not found"
            )

        # Find target deployment for rollback
        if rollback_data.target_deployment_id:
            target = db.query(DeploymentModel).filter(
                DeploymentModel.deployment_id == rollback_data.target_deployment_id
            ).first()
        else:
            target = DeploymentService.find_previous_deployment(
                current.entity_id,
                current.environment,
                deployment_id,
                db
            )

        if not target:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No previous deployment found to rollback to"
            )

        # Update current deployment
        current.status = 'rolled_back'
        current.rolled_back_at = datetime.utcnow()
        current.rolled_back_by = rollback_data.rolled_back_by
        current.rollback_reason = rollback_data.reason
        current.previous_deployment_id = target.deployment_id

        # Reactivate target deployment
        target.status = 'active'

        # Update entity with target config
        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == current.entity_id
        ).first()

        if entity:
            entity.deployment_config = target.config_snapshot
            entity.deployed_at = datetime.utcnow()
            entity.deployed_by = rollback_data.rolled_back_by

        db.commit()
        db.refresh(current)

        logger.info(
            f"Rolled back deployment {deployment_id} "
            f"to {target.deployment_id} in {current.environment}"
        )

        # Publish NATS event
        try:
            await publisher.publish_generic_event(
                event_type=EventType.DEPLOYMENT_ROLLED_BACK,
                subject=Subjects.DEPLOYMENT_ALL,
                data={
                    "deployment_id": str(deployment_id),
                    "target_deployment_id": str(target.deployment_id),
                    "environment": current.environment,
                    "reason": rollback_data.reason,
                    "rolled_back_by": rollback_data.rolled_back_by
                },
                deployment_id=str(deployment_id)
            )
        except Exception as e:
            logger.error(f"Failed to publish rollback event: {e}")

        return DeploymentResponse.model_validate(current)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back deployment: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== GET ENTITY DEPLOYMENTS ====================

@router.get("/entity/{entity_id}/deployments", response_model=DeploymentList)
async def get_entity_deployments(
    entity_id: UUID,
    environment: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> DeploymentList:
    """Get all deployments for a specific entity."""
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

        # Build query
        query = db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == entity_id
        )

        if environment:
            query = query.filter(DeploymentModel.environment == environment)

        if status:
            query = query.filter(DeploymentModel.status == status)

        total = query.count()

        offset = (page - 1) * page_size
        deployments = query.order_by(DeploymentModel.deployed_at.desc()) \
                          .offset(offset) \
                          .limit(page_size) \
                          .all()

        return DeploymentList(
            deployments=[DeploymentResponse.model_validate(d) for d in deployments],
            total=total,
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity deployments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
