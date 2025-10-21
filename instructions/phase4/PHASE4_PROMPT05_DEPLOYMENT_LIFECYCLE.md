# PHASE 4 - PROMPT 05: Deployment Lifecycle
# Entity Deployment and Rollback System

**Task ID**: PHASE4_PROMPT05
**Estimated Time**: 3-4 hours
**Component**: Deployment Lifecycle Management
**Dependencies**: PHASE4_PROMPT04 (Entity CRUD must be working)

---

## 🎯 OBJECTIVE

**Build COMPLETE deployment lifecycle management for entities.**

This includes:
- POST /deployments - Deploy entity to environment
- GET /deployments - List deployments with filters
- GET /deployments/{id} - Get deployment details
- POST /deployments/{id}/rollback - Rollback deployment
- GET /entities/{id}/deployments - Get entity's deployments
- Pre-deployment validation
- Post-deployment validation
- Deployment status tracking
- NATS event publishing

**This enables controlled entity deployment with rollback capability. No shortcuts.**

---

## ⚠️ MANDATORY PRINCIPLES

### Component Isolation
- **FIX ERRORS WITHIN THIS COMPONENT ONLY**
- Do NOT modify entity endpoints
- Do NOT change database schema
- Deployment logic stays within deployment router

### Comprehensive Implementation
- ✅ FULL deployment validation (pre and post)
- ✅ ALL deployment statuses tracked
- ✅ COMPLETE rollback capability
- ✅ ALL error cases handled
- ✅ COMPREHENSIVE logging

---

## 📋 VALIDATION GATE

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# 1. Entity CRUD working
curl -s "http://localhost:8350/api/v1/entities" | jq -e '.total >= 0' && \
    echo "✅ Entity API working" || echo "❌ RUN PROMPT04 FIRST"

# 2. Can create test entity
TEST_ENTITY=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"deploy_test_'$(date +%s)'","type":"strategy","version":"1.0.0"}')

ENTITY_ID=$(echo "$TEST_ENTITY" | jq -r '.entity_id')
test -n "$ENTITY_ID" && echo "✅ Can create entities ($ENTITY_ID)" || echo "❌ ENTITY CREATE FAILED"

# 3. Database has deployments table
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT COUNT(*) FROM deployments;" > /dev/null 2>&1 && \
    echo "✅ Deployments table exists" || echo "❌ TABLE MISSING"

# 4. NATS working
curl -s http://localhost:8350/health/detailed | grep -q "nats" && \
    echo "✅ NATS integrated" || echo "⚠️ NATS may not be working"
```

**STOP if validation fails.**

---

## 🏗️ IMPLEMENTATION

### STEP 1: Create Deployment Schemas

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\library\apps\library

cat > src/schemas/deployment.py << 'EOF'
"""
Pydantic schemas for Deployment API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class DeploymentEnvironment(str, Enum):
    """Deployment environment enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DeploymentStatus(str, Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentCreate(BaseModel):
    """Schema for creating deployment."""
    entity_id: UUID
    environment: DeploymentEnvironment
    deployed_by: str = Field(..., min_length=1, max_length=255)
    deployment_method: Optional[str] = Field(None, max_length=50)
    config_override: Optional[Dict[str, Any]] = Field(default_factory=dict)
    parameters_override: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DeploymentUpdate(BaseModel):
    """Schema for updating deployment."""
    status: Optional[DeploymentStatus] = None
    error_logs: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(extra='forbid')


class DeploymentResponse(BaseModel):
    """Schema for deployment response."""
    deployment_id: UUID
    entity_id: UUID
    version: str
    environment: DeploymentEnvironment
    config_snapshot: Dict[str, Any]
    parameters_snapshot: Optional[Dict[str, Any]]
    status: DeploymentStatus
    deployed_at: datetime
    deployed_by: str
    deployment_method: Optional[str]
    rolled_back_at: Optional[datetime]
    rolled_back_by: Optional[str]
    rollback_reason: Optional[str]
    previous_deployment_id: Optional[UUID]
    health_checks: list
    last_health_check: Optional[datetime]
    error_logs: Optional[str]
    deployment_duration_seconds: Optional[int]
    validation_results: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DeploymentList(BaseModel):
    """Schema for list of deployments."""
    deployments: list[DeploymentResponse]
    total: int
    page: int
    page_size: int


class RollbackRequest(BaseModel):
    """Schema for rollback request."""
    reason: str = Field(..., min_length=1)
    rolled_back_by: str = Field(..., min_length=1, max_length=255)
    target_deployment_id: Optional[UUID] = Field(
        None, 
        description="Specific deployment to rollback to (if not provided, uses previous)"
    )


class DeploymentValidation(BaseModel):
    """Schema for deployment validation results."""
    passed: bool
    checks: Dict[str, Any]
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
EOF

echo "✅ Deployment schemas created"
```

---

### STEP 2: Create Deployment Service

```bash
cat > src/services/deployment_service.py << 'EOF'
"""
Deployment service with validation and lifecycle management.
"""
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from datetime import datetime
from typing import Optional, Tuple

from ..db.models import Entity as EntityModel, Deployment as DeploymentModel
from ..schemas.deployment import DeploymentValidation

logger = logging.getLogger(__name__)


class DeploymentService:
    """Service for deployment operations."""
    
    @staticmethod
    def validate_pre_deployment(
        entity: EntityModel,
        environment: str,
        db: Session
    ) -> DeploymentValidation:
        """
        Validate entity before deployment.
        
        Checks:
        - Entity exists and not deleted
        - Entity is in validated or registered status
        - No active deployment in target environment
        - Dependencies are met
        """
        errors = []
        warnings = []
        checks = {}
        
        # Check 1: Entity status
        if entity.status not in ['registered', 'validated', 'deployed', 'active']:
            errors.append(f"Entity status '{entity.status}' not deployable")
        checks['entity_status'] = entity.status
        
        # Check 2: Existing active deployment in environment
        existing = db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == entity.entity_id,
            DeploymentModel.environment == environment,
            DeploymentModel.status == 'active'
        ).first()
        
        if existing:
            warnings.append(f"Active deployment already exists in {environment}")
        checks['existing_deployment'] = existing is not None
        
        # Check 3: Entity health
        if entity.health_status == 'unhealthy':
            errors.append("Entity health is unhealthy")
        checks['health_status'] = entity.health_status
        
        # Check 4: Required fields
        if not entity.version:
            errors.append("Entity version is required")
        checks['has_version'] = entity.version is not None
        
        passed = len(errors) == 0
        
        return DeploymentValidation(
            passed=passed,
            checks=checks,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_post_deployment(
        deployment: DeploymentModel,
        db: Session
    ) -> DeploymentValidation:
        """
        Validate deployment after execution.
        
        Checks:
        - Deployment record created
        - Entity status updated
        - Configuration snapshot saved
        """
        errors = []
        warnings = []
        checks = {}
        
        # Check 1: Deployment exists
        checks['deployment_exists'] = deployment is not None
        
        # Check 2: Has config snapshot
        if not deployment.config_snapshot:
            warnings.append("No configuration snapshot saved")
        checks['has_config'] = deployment.config_snapshot is not None
        
        # Check 3: Status appropriate
        if deployment.status not in ['active', 'deploying']:
            errors.append(f"Deployment status '{deployment.status}' unexpected")
        checks['status'] = deployment.status
        
        passed = len(errors) == 0
        
        return DeploymentValidation(
            passed=passed,
            checks=checks,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def find_previous_deployment(
        entity_id: UUID,
        environment: str,
        current_deployment_id: UUID,
        db: Session
    ) -> Optional[DeploymentModel]:
        """Find the previous active deployment for rollback."""
        return db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == entity_id,
            DeploymentModel.environment == environment,
            DeploymentModel.status == 'active',
            DeploymentModel.deployment_id != current_deployment_id,
            DeploymentModel.deployed_at < db.query(DeploymentModel.deployed_at).filter(
                DeploymentModel.deployment_id == current_deployment_id
            ).scalar_subquery()
        ).order_by(DeploymentModel.deployed_at.desc()).first()
EOF

echo "✅ Deployment service created"
```

---

### STEP 3: Create Deployment Endpoints

```bash
cat > src/api/v1/endpoints/deployments.py << 'EOF'
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
EOF

echo "✅ Deployment endpoints created"
```

---

### STEP 4: Update API Router

```bash
cat >> src/api/v1/__init__.py << 'EOF'

# Add deployment router
from .endpoints import deployments

api_router.include_router(deployments.router)
EOF

echo "✅ API router updated"
```

---

## 🧪 COMPREHENSIVE TESTING

### TEST 1: Deploy Entity

```bash
# Get entity to deploy
ENTITY_ID=$(curl -s "http://localhost:8350/api/v1/entities" | jq -r '.entities[0].entity_id')

# Deploy to staging
curl -X POST "http://localhost:8350/api/v1/deployments" \
  -H "Content-Type: application/json" \
  -d "{
    \"entity_id\": \"$ENTITY_ID\",
    \"environment\": \"staging\",
    \"deployed_by\": \"test_user\"
  }" | jq '.'

# Verify deployment created
curl -s "http://localhost:8350/api/v1/deployments?entity_id=$ENTITY_ID" | jq '.'
```

### TEST 2: Rollback

```bash
# Get deployment ID
DEPLOY_ID=$(curl -s "http://localhost:8350/api/v1/deployments?entity_id=$ENTITY_ID&status=active" | \
    jq -r '.deployments[0].deployment_id')

# Rollback
curl -X POST "http://localhost:8350/api/v1/deployments/$DEPLOY_ID/rollback" \
  -H "Content-Type: application/json" \
  -d "{
    \"reason\": \"Testing rollback\",
    \"rolled_back_by\": \"test_user\"
  }" | jq '.'
```

### TEST 3: Integration

```bash
# Full deployment cycle
echo "1. Create entity"
ENTITY=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"deploy_cycle_test","type":"strategy","version":"1.0.0"}')
EID=$(echo "$ENTITY" | jq -r '.entity_id')

echo "2. Deploy to staging"
DEPLOY=$(curl -s -X POST "http://localhost:8350/api/v1/deployments" \
  -H "Content-Type: application/json" \
  -d "{\"entity_id\":\"$EID\",\"environment\":\"staging\",\"deployed_by\":\"test\"}")
DID=$(echo "$DEPLOY" | jq -r '.deployment_id')

echo "3. Verify entity status updated"
curl -s "http://localhost:8350/api/v1/entities/$EID" | jq '.status'

echo "4. Rollback"
curl -X POST "http://localhost:8350/api/v1/deployments/$DID/rollback" \
  -H "Content-Type: application/json" \
  -d '{"reason":"test","rolled_back_by":"test"}' | jq '.status'

echo "✅ Full cycle complete"
```

---

## ✅ SUCCESS CRITERIA

- [ ] Can deploy entity to environment
- [ ] Pre-deployment validation working
- [ ] Post-deployment validation working
- [ ] Existing deployments deactivated
- [ ] Entity status updated on deployment
- [ ] Can rollback deployment
- [ ] Previous deployment reactivated on rollback
- [ ] NATS events published
- [ ] Validation errors caught
- [ ] Cannot deploy unhealthy entities

---

**NEXT PROMPT**: PHASE4_PROMPT06_HOTSWAP_ENGINE.md
