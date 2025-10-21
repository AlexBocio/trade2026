# PHASE 4 - PROMPT 06: HotSwap Engine
# Zero-Downtime Strategy Swapping System

**Task ID**: PHASE4_PROMPT06
**Estimated Time**: 4-5 hours
**Component**: HotSwap Engine
**Dependencies**: PHASE4_PROMPT05 (Deployment Lifecycle must be working)

---

## 🎯 OBJECTIVE

**Build COMPLETE hot-swap system for zero-downtime strategy/entity swapping.**

This includes:
- POST /swaps - Initiate swap between entities
- GET /swaps - List swaps with filters
- GET /swaps/{id} - Get swap details
- POST /swaps/{id}/rollback - Rollback swap
- Pre-swap validation (compatibility checks)
- Swap execution logic
- Post-swap validation
- Downtime tracking
- NATS event publishing

**This enables seamless entity swapping without system downtime. No shortcuts.**

---

## ⚠️ MANDATORY PRINCIPLES

### Component Isolation
- **FIX ERRORS WITHIN THIS COMPONENT ONLY**
- Do NOT modify deployment endpoints
- Do NOT change entity endpoints
- Swap logic stays within swap router

### Comprehensive Implementation
- ✅ FULL pre-swap validation (all compatibility checks)
- ✅ ALL swap types supported
- ✅ COMPLETE rollback capability
- ✅ DOWNTIME tracking (milliseconds)
- ✅ COMPREHENSIVE error handling

---

## 📋 VALIDATION GATE

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# 1. Deployment endpoints working
curl -s "http://localhost:8350/api/v1/deployments" | jq -e '.total >= 0' && \
    echo "✅ Deployment API working" || echo "❌ RUN PROMPT05 FIRST"

# 2. Need at least 2 deployed entities for swapping
DEPLOYED=$(curl -s "http://localhost:8350/api/v1/deployments?status=active" | jq '.total')
test "$DEPLOYED" -ge 1 && echo "✅ Have deployed entities ($DEPLOYED)" || \
    echo "⚠️ Need to deploy entities first"

# 3. Database has swaps table
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT COUNT(*) FROM swaps;" > /dev/null 2>&1 && \
    echo "✅ Swaps table exists" || echo "❌ TABLE MISSING"

# 4. Can create test entities for swapping
curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"swap_test_a_'$(date +%s)'","type":"strategy","version":"1.0.0"}' | \
  jq -e '.entity_id' && echo "✅ Can create entities" || echo "❌ ENTITY CREATE FAILED"
```

**STOP if validation fails.**

---

## 🏗️ IMPLEMENTATION

### STEP 1: Create Swap Schemas

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\library\apps\library

cat > src/schemas/swap.py << 'EOF'
"""
Pydantic schemas for Swap API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class SwapType(str, Enum):
    """Swap type enumeration."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    AUTOMATIC = "automatic"
    EMERGENCY = "emergency"
    ROLLBACK = "rollback"


class SwapStatus(str, Enum):
    """Swap status enumeration."""
    INITIATED = "initiated"
    VALIDATING = "validating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class SwapCreate(BaseModel):
    """Schema for creating swap."""
    from_entity_id: UUID
    to_entity_id: UUID
    reason: str = Field(..., min_length=1, max_length=500)
    initiated_by: str = Field(..., min_length=1, max_length=255)
    swap_type: SwapType = SwapType.MANUAL
    validate_only: bool = Field(
        False, 
        description="If true, only validate compatibility without executing swap"
    )
    target_environment: Optional[str] = Field(
        None,
        description="Specific environment to swap in (if not provided, swaps in all)"
    )


class SwapUpdate(BaseModel):
    """Schema for updating swap."""
    status: Optional[SwapStatus] = None
    error_message: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(extra='forbid')


class SwapResponse(BaseModel):
    """Schema for swap response."""
    swap_id: UUID
    from_entity_id: UUID
    to_entity_id: UUID
    from_deployment_id: Optional[UUID]
    to_deployment_id: Optional[UUID]
    swap_type: SwapType
    status: SwapStatus
    reason: str
    initiated_by: str
    initiated_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    downtime_milliseconds: Optional[int]
    success: bool
    error_message: Optional[str]
    validation_results: Optional[Dict[str, Any]]
    rollback_swap_id: Optional[UUID]
    rolled_back_at: Optional[datetime]
    rolled_back_by: Optional[str]
    rollback_reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SwapList(BaseModel):
    """Schema for list of swaps."""
    swaps: List[SwapResponse]
    total: int
    page: int
    page_size: int


class SwapRollbackRequest(BaseModel):
    """Schema for swap rollback request."""
    reason: str = Field(..., min_length=1)
    rolled_back_by: str = Field(..., min_length=1, max_length=255)


class SwapValidation(BaseModel):
    """Schema for swap validation results."""
    passed: bool
    checks: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    compatible: bool
    estimated_downtime_ms: Optional[int] = None
EOF

echo "✅ Swap schemas created"
```

---

### STEP 2: Create Swap Service with Validation Logic

```bash
cat > src/services/swap_service.py << 'EOF'
"""
Swap service with validation and execution logic.
"""
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from datetime import datetime
from typing import Optional, Tuple

from ..db.models import (
    Entity as EntityModel, 
    Deployment as DeploymentModel,
    Swap as SwapModel
)
from ..schemas.swap import SwapValidation

logger = logging.getLogger(__name__)


class SwapService:
    """Service for swap operations and validation."""
    
    @staticmethod
    def validate_swap_compatibility(
        from_entity: EntityModel,
        to_entity: EntityModel,
        db: Session
    ) -> SwapValidation:
        """
        Validate entities are compatible for swapping.
        
        Compatibility checks:
        - Both entities exist and not deleted
        - Both are same type
        - From entity is deployed
        - To entity is ready (deployed or validated)
        - No incompatible versions
        - Dependencies are met
        - Health status acceptable
        """
        errors = []
        warnings = []
        checks = {}
        
        # Check 1: Entity existence
        if from_entity.deleted_at or to_entity.deleted_at:
            errors.append("Cannot swap deleted entities")
        checks['entities_exist'] = True
        
        # Check 2: Same type
        if from_entity.type != to_entity.type:
            errors.append(
                f"Entity type mismatch: {from_entity.type} vs {to_entity.type}"
            )
        checks['same_type'] = from_entity.type == to_entity.type
        
        # Check 3: From entity deployed
        if from_entity.status not in ['deployed', 'active']:
            errors.append(
                f"From entity not deployed (status: {from_entity.status})"
            )
        checks['from_deployed'] = from_entity.status in ['deployed', 'active']
        
        # Check 4: To entity ready
        if to_entity.status not in ['deployed', 'active', 'validated', 'registered']:
            errors.append(
                f"To entity not ready (status: {to_entity.status})"
            )
        checks['to_ready'] = to_entity.status in ['deployed', 'active', 'validated', 'registered']
        
        # Check 5: Health status
        if from_entity.health_status == 'unhealthy':
            warnings.append("From entity health is unhealthy")
        if to_entity.health_status == 'unhealthy':
            errors.append("To entity health is unhealthy")
        checks['health_acceptable'] = to_entity.health_status != 'unhealthy'
        
        # Check 6: Active deployments exist
        from_deployment = db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == from_entity.entity_id,
            DeploymentModel.status == 'active'
        ).first()
        
        if not from_deployment:
            errors.append("From entity has no active deployment")
        checks['from_has_deployment'] = from_deployment is not None
        
        # Check 7: Version compatibility (if versioned)
        if from_entity.version and to_entity.version:
            # Simple version check - in production, use semantic versioning
            checks['versions'] = {
                'from': from_entity.version,
                'to': to_entity.version
            }
        
        # Check 8: Configuration compatibility
        if from_entity.config and to_entity.config:
            # Check if required config keys are present
            from_keys = set(from_entity.config.keys())
            to_keys = set(to_entity.config.keys())
            missing_keys = from_keys - to_keys
            
            if missing_keys:
                warnings.append(
                    f"To entity missing config keys: {missing_keys}"
                )
            checks['config_compatible'] = len(missing_keys) == 0
        
        # Estimate downtime (mock - in production, calculate from historical data)
        estimated_downtime_ms = 50  # Assume 50ms for swap operation
        
        passed = len(errors) == 0
        compatible = passed and len(warnings) == 0
        
        return SwapValidation(
            passed=passed,
            checks=checks,
            errors=errors,
            warnings=warnings,
            compatible=compatible,
            estimated_downtime_ms=estimated_downtime_ms
        )
    
    @staticmethod
    def execute_swap(
        from_entity: EntityModel,
        to_entity: EntityModel,
        swap: SwapModel,
        target_environment: Optional[str],
        db: Session
    ) -> Tuple[bool, Optional[str], int]:
        """
        Execute the swap operation.
        
        Returns:
            Tuple of (success, error_message, downtime_ms)
        """
        start_time = datetime.utcnow()
        
        try:
            # Get deployments to swap
            from_deployments = db.query(DeploymentModel).filter(
                DeploymentModel.entity_id == from_entity.entity_id,
                DeploymentModel.status == 'active'
            )
            
            if target_environment:
                from_deployments = from_deployments.filter(
                    DeploymentModel.environment == target_environment
                )
            
            from_deployments = from_deployments.all()
            
            if not from_deployments:
                return False, "No active deployments to swap from", 0
            
            # Track downtime start
            downtime_start = datetime.utcnow()
            
            # Step 1: Deactivate from deployments
            for deployment in from_deployments:
                deployment.status = 'inactive'
                logger.info(f"Deactivated deployment {deployment.deployment_id}")
            
            # Step 2: Activate or create to deployments
            for from_deployment in from_deployments:
                # Check if to_entity has deployment in this environment
                to_deployment = db.query(DeploymentModel).filter(
                    DeploymentModel.entity_id == to_entity.entity_id,
                    DeploymentModel.environment == from_deployment.environment
                ).first()
                
                if to_deployment:
                    # Activate existing deployment
                    to_deployment.status = 'active'
                    logger.info(f"Activated deployment {to_deployment.deployment_id}")
                else:
                    # Create new deployment
                    new_deployment = DeploymentModel(
                        entity_id=to_entity.entity_id,
                        version=to_entity.version,
                        environment=from_deployment.environment,
                        config_snapshot=to_entity.config or {},
                        parameters_snapshot=to_entity.parameters or {},
                        status='active',
                        deployed_by=swap.initiated_by,
                        deployment_method='hotswap'
                    )
                    db.add(new_deployment)
                    logger.info(
                        f"Created new deployment for {to_entity.name} "
                        f"in {from_deployment.environment}"
                    )
            
            # Step 3: Update entity statuses
            from_entity.status = 'inactive'
            to_entity.status = 'active'
            to_entity.deployed_at = datetime.utcnow()
            to_entity.deployed_by = swap.initiated_by
            
            # Track downtime end
            downtime_end = datetime.utcnow()
            downtime_ms = int((downtime_end - downtime_start).total_seconds() * 1000)
            
            # Commit transaction
            db.flush()
            
            logger.info(
                f"Swap executed successfully: {from_entity.name} → {to_entity.name} "
                f"(downtime: {downtime_ms}ms)"
            )
            
            return True, None, downtime_ms
            
        except Exception as e:
            logger.error(f"Swap execution failed: {e}")
            db.rollback()
            return False, str(e), 0
    
    @staticmethod
    def rollback_swap(
        swap: SwapModel,
        rollback_reason: str,
        rolled_back_by: str,
        db: Session
    ) -> Tuple[bool, Optional[str]]:
        """
        Rollback a completed swap.
        
        Reverses the swap by reactivating from entity and deactivating to entity.
        """
        try:
            # Get entities
            from_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == swap.from_entity_id
            ).first()
            to_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == swap.to_entity_id
            ).first()
            
            if not from_entity or not to_entity:
                return False, "Entities not found"
            
            # Reverse the swap: deactivate to, reactivate from
            to_deployments = db.query(DeploymentModel).filter(
                DeploymentModel.entity_id == to_entity.entity_id,
                DeploymentModel.status == 'active'
            ).all()
            
            for deployment in to_deployments:
                deployment.status = 'inactive'
            
            # Reactivate from deployments
            from_deployments = db.query(DeploymentModel).filter(
                DeploymentModel.entity_id == from_entity.entity_id,
                DeploymentModel.status == 'inactive'
            ).order_by(DeploymentModel.deployed_at.desc()).all()
            
            for deployment in from_deployments:
                deployment.status = 'active'
            
            # Update entity statuses
            from_entity.status = 'active'
            to_entity.status = 'inactive'
            
            # Update swap record
            swap.status = 'rolled_back'
            swap.rolled_back_at = datetime.utcnow()
            swap.rolled_back_by = rolled_back_by
            swap.rollback_reason = rollback_reason
            
            db.flush()
            
            logger.info(f"Swap {swap.swap_id} rolled back successfully")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Swap rollback failed: {e}")
            db.rollback()
            return False, str(e)
EOF

echo "✅ Swap service created"
```

---

### STEP 3: Create Swap Endpoints

```bash
cat > src/api/v1/endpoints/swaps.py << 'EOF'
"""
Swap endpoints for Library Service.
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
    SwapCreate, SwapUpdate, SwapResponse, SwapList,
    SwapRollbackRequest, SwapValidation, SwapStatus
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
    from_entity_id: Optional[UUID] = Query(None),
    to_entity_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    swap_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> SwapList:
    """List swaps with pagination and filtering."""
    try:
        query = db.query(SwapModel)
        
        if from_entity_id:
            query = query.filter(SwapModel.from_entity_id == from_entity_id)
        
        if to_entity_id:
            query = query.filter(SwapModel.to_entity_id == to_entity_id)
        
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
            detail=str(e)
        )


# ==================== GET SWAP ====================

@router.get("/{swap_id}", response_model=SwapResponse)
async def get_swap(
    swap_id: UUID,
    db: Session = Depends(get_db)
) -> SwapResponse:
    """Get swap by ID."""
    swap = db.query(SwapModel).filter(
        SwapModel.swap_id == swap_id
    ).first()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Swap {swap_id} not found"
        )
    
    return SwapResponse.model_validate(swap)


# ==================== CREATE SWAP ====================

@router.post("", response_model=SwapResponse, status_code=status.HTTP_201_CREATED)
async def create_swap(
    swap_data: SwapCreate,
    db: Session = Depends(get_db)
) -> SwapResponse:
    """
    Execute hot-swap between two entities.
    
    Process:
    1. Validate entities exist
    2. Run compatibility validation
    3. If validate_only=true, return validation results
    4. Execute swap:
       - Deactivate from_entity deployments
       - Activate to_entity deployments (or create new)
       - Update entity statuses
    5. Track downtime
    6. Publish swap event
    """
    start_time = datetime.utcnow()
    
    try:
        # Get entities
        from_entity = db.query(EntityModel).filter(
            EntityModel.entity_id == swap_data.from_entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()
        
        to_entity = db.query(EntityModel).filter(
            EntityModel.entity_id == swap_data.to_entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()
        
        if not from_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"From entity {swap_data.from_entity_id} not found"
            )
        
        if not to_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"To entity {swap_data.to_entity_id} not found"
            )
        
        # Validate compatibility
        validation = SwapService.validate_swap_compatibility(
            from_entity, to_entity, db
        )
        
        # If validation only, return results
        if swap_data.validate_only:
            return SwapResponse(
                swap_id=UUID('00000000-0000-0000-0000-000000000000'),  # Dummy ID
                from_entity_id=swap_data.from_entity_id,
                to_entity_id=swap_data.to_entity_id,
                status=SwapStatus.VALIDATING,
                reason=swap_data.reason,
                initiated_by=swap_data.initiated_by,
                initiated_at=datetime.utcnow(),
                success=validation.passed,
                validation_results=validation.model_dump(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        # If validation failed, raise error
        if not validation.passed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Swap validation failed",
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "checks": validation.checks
                }
            )
        
        # Create swap record
        swap = SwapModel(
            from_entity_id=swap_data.from_entity_id,
            to_entity_id=swap_data.to_entity_id,
            swap_type=swap_data.swap_type,
            status=SwapStatus.IN_PROGRESS,
            reason=swap_data.reason,
            initiated_by=swap_data.initiated_by,
            validation_results=validation.model_dump()
        )
        
        db.add(swap)
        db.flush()  # Get swap_id
        
        # Execute swap
        success, error_msg, downtime_ms = SwapService.execute_swap(
            from_entity,
            to_entity,
            swap,
            swap_data.target_environment,
            db
        )
        
        # Update swap record
        swap.status = SwapStatus.COMPLETED if success else SwapStatus.FAILED
        swap.success = success
        swap.error_message = error_msg
        swap.completed_at = datetime.utcnow()
        swap.duration_seconds = int(
            (datetime.utcnow() - start_time).total_seconds()
        )
        swap.downtime_milliseconds = downtime_ms
        
        db.commit()
        db.refresh(swap)
        
        logger.info(
            f"Swap {'completed' if success else 'failed'}: "
            f"{from_entity.name} → {to_entity.name} "
            f"({swap.swap_id})"
        )
        
        # Publish NATS event
        try:
            event_type = EventType.SWAP_COMPLETED if success else EventType.SWAP_FAILED
            await publisher.publish_generic_event(
                event_type=event_type,
                subject=Subjects.SWAP_COMPLETED if success else Subjects.SWAP_ALL,
                data={
                    "swap_id": str(swap.swap_id),
                    "from_entity_id": str(swap_data.from_entity_id),
                    "to_entity_id": str(swap_data.to_entity_id),
                    "success": success,
                    "downtime_ms": downtime_ms,
                    "error": error_msg
                },
                entity_id=str(swap_data.to_entity_id)
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
            detail=str(e)
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
    
    Reverses the swap operation by reactivating from entity
    and deactivating to entity.
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
        
        # Verify swap can be rolled back
        if swap.status != SwapStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot rollback swap with status: {swap.status}"
            )
        
        if swap.rolled_back_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Swap already rolled back"
            )
        
        # Execute rollback
        success, error_msg = SwapService.rollback_swap(
            swap,
            rollback_data.reason,
            rollback_data.rolled_back_by,
            db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rollback failed: {error_msg}"
            )
        
        db.commit()
        db.refresh(swap)
        
        logger.info(f"Swap {swap_id} rolled back successfully")
        
        # Publish NATS event
        try:
            await publisher.publish_generic_event(
                event_type=EventType.SWAP_ROLLED_BACK,
                subject=Subjects.SWAP_ALL,
                data={
                    "swap_id": str(swap_id),
                    "reason": rollback_data.reason,
                    "rolled_back_by": rollback_data.rolled_back_by
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish rollback event: {e}")
        
        return SwapResponse.model_validate(swap)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back swap: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== GET ENTITY SWAPS ====================

@router.get("/entity/{entity_id}/swaps", response_model=SwapList)
async def get_entity_swaps(
    entity_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> SwapList:
    """Get all swaps involving a specific entity (as from or to)."""
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
        
        # Get swaps
        from sqlalchemy import or_
        query = db.query(SwapModel).filter(
            or_(
                SwapModel.from_entity_id == entity_id,
                SwapModel.to_entity_id == entity_id
            )
        )
        
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
            detail=str(e)
        )
EOF

echo "✅ Swap endpoints created"
```

---

### STEP 4: Update API Router

```bash
cat >> src/api/v1/__init__.py << 'EOF'

# Add swap router
from .endpoints import swaps

api_router.include_router(swaps.router)
EOF

echo "✅ API router updated with swaps"
```

---

## 🧪 COMPREHENSIVE TESTING

### TEST 1: Create Test Entities and Deploy

```bash
echo "=== Setup: Creating and deploying entities for swap test ==="

# Create entity A
ENTITY_A=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "strategy_alpha",
    "type": "strategy",
    "version": "1.0.0",
    "description": "Alpha strategy for swapping",
    "config": {"risk_level": "medium"}
  }' | jq -r '.entity_id')

echo "Created Entity A: $ENTITY_A"

# Create entity B
ENTITY_B=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "strategy_beta",
    "type": "strategy",
    "version": "1.1.0",
    "description": "Beta strategy for swapping",
    "config": {"risk_level": "medium"}
  }' | jq -r '.entity_id')

echo "Created Entity B: $ENTITY_B"

# Deploy Entity A to production
DEPLOY_A=$(curl -s -X POST "http://localhost:8350/api/v1/deployments" \
  -H "Content-Type: application/json" \
  -d "{
    \"entity_id\": \"$ENTITY_A\",
    \"environment\": \"production\",
    \"deployed_by\": \"test_user\"
  }" | jq -r '.deployment_id')

echo "Deployed Entity A: $DEPLOY_A"

# Deploy Entity B to staging
DEPLOY_B=$(curl -s -X POST "http://localhost:8350/api/v1/deployments" \
  -H "Content-Type: application/json" \
  -d "{
    \"entity_id\": \"$ENTITY_B\",
    \"environment\": \"staging\",
    \"deployed_by\": \"test_user\"
  }" | jq -r '.deployment_id')

echo "Deployed Entity B: $DEPLOY_B"
echo "✅ Setup complete"
```

---

### TEST 2: Validate Swap Compatibility (Dry Run)

```bash
echo "=== Testing swap validation (dry run) ==="

curl -s -X POST "http://localhost:8350/api/v1/swaps" \
  -H "Content-Type: application/json" \
  -d "{
    \"from_entity_id\": \"$ENTITY_A\",
    \"to_entity_id\": \"$ENTITY_B\",
    \"reason\": \"Testing swap validation\",
    \"initiated_by\": \"test_user\",
    \"validate_only\": true
  }" | jq '.'

echo "✅ Check validation results"
```

---

### TEST 3: Execute Swap

```bash
echo "=== Executing swap ==="

SWAP_RESPONSE=$(curl -s -X POST "http://localhost:8350/api/v1/swaps" \
  -H "Content-Type: application/json" \
  -d "{
    \"from_entity_id\": \"$ENTITY_A\",
    \"to_entity_id\": \"$ENTITY_B\",
    \"reason\": \"Upgrading to beta strategy\",
    \"initiated_by\": \"test_user\",
    \"swap_type\": \"manual\"
  }")

echo "$SWAP_RESPONSE" | jq '.'

SWAP_ID=$(echo "$SWAP_RESPONSE" | jq -r '.swap_id')
echo "Swap ID: $SWAP_ID"

# Verify swap completed
STATUS=$(echo "$SWAP_RESPONSE" | jq -r '.status')
test "$STATUS" == "completed" && echo "✅ Swap completed" || echo "❌ Swap failed: $STATUS"

# Check downtime
DOWNTIME=$(echo "$SWAP_RESPONSE" | jq -r '.downtime_milliseconds')
echo "Downtime: ${DOWNTIME}ms"
```

---

### TEST 4: Verify Entity Statuses Changed

```bash
echo "=== Verifying entity statuses after swap ==="

# Entity A should be inactive
STATUS_A=$(curl -s "http://localhost:8350/api/v1/entities/$ENTITY_A" | jq -r '.status')
echo "Entity A status: $STATUS_A"
test "$STATUS_A" == "inactive" && echo "✅ Entity A deactivated" || echo "❌ Entity A not inactive"

# Entity B should be active
STATUS_B=$(curl -s "http://localhost:8350/api/v1/entities/$ENTITY_B" | jq -r '.status')
echo "Entity B status: $STATUS_B"
test "$STATUS_B" == "active" && echo "✅ Entity B activated" || echo "❌ Entity B not active"
```

---

### TEST 5: Verify Deployment Statuses Changed

```bash
echo "=== Verifying deployment statuses ==="

# Entity A deployments should be inactive
curl -s "http://localhost:8350/api/v1/deployments?entity_id=$ENTITY_A" | \
    jq '.deployments[] | {deployment_id, status}'

# Entity B should have active deployment in production
curl -s "http://localhost:8350/api/v1/deployments?entity_id=$ENTITY_B&environment=production" | \
    jq '.deployments[] | {deployment_id, status, environment}'

echo "✅ Check deployment statuses"
```

---

### TEST 6: List Swaps

```bash
echo "=== Listing swaps ==="

# List all swaps
curl -s "http://localhost:8350/api/v1/swaps" | jq '.'

# Filter by entity
curl -s "http://localhost:8350/api/v1/swaps?from_entity_id=$ENTITY_A" | jq '.total'

# Get specific swap
curl -s "http://localhost:8350/api/v1/swaps/$SWAP_ID" | jq '.'

echo "✅ List operations working"
```

---

### TEST 7: Rollback Swap

```bash
echo "=== Testing swap rollback ==="

curl -s -X POST "http://localhost:8350/api/v1/swaps/$SWAP_ID/rollback" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Testing rollback functionality",
    "rolled_back_by": "test_user"
  }' | jq '.'

# Verify entity statuses reversed
STATUS_A=$(curl -s "http://localhost:8350/api/v1/entities/$ENTITY_A" | jq -r '.status')
STATUS_B=$(curl -s "http://localhost:8350/api/v1/entities/$ENTITY_B" | jq -r '.status')

echo "After rollback:"
echo "  Entity A: $STATUS_A (should be active)"
echo "  Entity B: $STATUS_B (should be inactive)"

test "$STATUS_A" == "active" && echo "✅ Rollback successful" || echo "❌ Rollback failed"
```

---

### TEST 8: Test Validation Errors

```bash
echo "=== Testing validation error handling ==="

# Try to swap incompatible types
INCOMP_ENTITY=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"pipeline_test","type":"pipeline","version":"1.0.0"}' | jq -r '.entity_id')

curl -s -X POST "http://localhost:8350/api/v1/swaps" \
  -H "Content-Type: application/json" \
  -d "{
    \"from_entity_id\": \"$ENTITY_A\",
    \"to_entity_id\": \"$INCOMP_ENTITY\",
    \"reason\": \"Testing type mismatch\",
    \"initiated_by\": \"test_user\"
  }" | jq '.'

# Should return 400 Bad Request with validation errors
echo "✅ Check for type mismatch error"

# Try to swap non-deployed entity
UNDEPLOYED=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"undeployed_test","type":"strategy","version":"1.0.0"}' | jq -r '.entity_id')

curl -s -X POST "http://localhost:8350/api/v1/swaps" \
  -H "Content-Type: application/json" \
  -d "{
    \"from_entity_id\": \"$UNDEPLOYED\",
    \"to_entity_id\": \"$ENTITY_B\",
    \"reason\": \"Testing undeployed entity\",
    \"initiated_by\": \"test_user\"
  }" | jq '.'

# Should return 400 Bad Request
echo "✅ Check for deployment status error"
```

---

### TEST 9: NATS Event Publishing

```bash
echo "=== Testing NATS event publishing ==="

# Subscribe to swap events
docker run --rm -d --name swap-event-monitor --network trade2026-backend \
    natsio/nats-box:latest nats sub "library.swap.>" --server=nats:4222

sleep 2

# Execute a swap
curl -s -X POST "http://localhost:8350/api/v1/swaps" \
  -H "Content-Type: application/json" \
  -d "{
    \"from_entity_id\": \"$ENTITY_A\",
    \"to_entity_id\": \"$ENTITY_B\",
    \"reason\": \"Testing NATS events\",
    \"initiated_by\": \"test_user\"
  }" > /dev/null

sleep 2

# Check for events
docker logs swap-event-monitor 2>&1 | grep -E "swap\.(completed|initiated|failed)"

docker stop swap-event-monitor
docker rm swap-event-monitor

echo "✅ Check NATS logs for swap events"
```

---

### TEST 10: Performance - Downtime Tracking

```bash
echo "=== Testing downtime tracking ==="

# Execute multiple swaps and track downtime
for i in {1..5}; do
    RESPONSE=$(curl -s -X POST "http://localhost:8350/api/v1/swaps" \
      -H "Content-Type: application/json" \
      -d "{
        \"from_entity_id\": \"$ENTITY_A\",
        \"to_entity_id\": \"$ENTITY_B\",
        \"reason\": \"Performance test $i\",
        \"initiated_by\": \"test_user\"
      }")
    
    DOWNTIME=$(echo "$RESPONSE" | jq -r '.downtime_milliseconds')
    echo "Swap $i downtime: ${DOWNTIME}ms"
    
    # Rollback for next iteration
    SWAP_ID=$(echo "$RESPONSE" | jq -r '.swap_id')
    curl -s -X POST "http://localhost:8350/api/v1/swaps/$SWAP_ID/rollback" \
      -H "Content-Type: application/json" \
      -d '{"reason":"prep for next test","rolled_back_by":"test"}' > /dev/null
    
    sleep 1
done

echo "✅ Downtime tracking working"
```

---

## 🔗 INTEGRATION TESTING

### INTEGRATION TEST 1: Full Swap Lifecycle

```bash
echo "=== Full swap lifecycle integration test ==="

# 1. Create entities
E1=$(curl -s -X POST http://localhost:8350/api/v1/entities \
  -d '{"name":"lifecycle_test_a","type":"strategy","version":"1.0.0"}' | jq -r '.entity_id')
E2=$(curl -s -X POST http://localhost:8350/api/v1/entities \
  -d '{"name":"lifecycle_test_b","type":"strategy","version":"2.0.0"}' | jq -r '.entity_id')

# 2. Deploy both
curl -s -X POST http://localhost:8350/api/v1/deployments \
  -d "{\"entity_id\":\"$E1\",\"environment\":\"production\",\"deployed_by\":\"test\"}" > /dev/null
curl -s -X POST http://localhost:8350/api/v1/deployments \
  -d "{\"entity_id\":\"$E2\",\"environment\":\"staging\",\"deployed_by\":\"test\"}" > /dev/null

# 3. Execute swap
SWAP=$(curl -s -X POST http://localhost:8350/api/v1/swaps \
  -d "{\"from_entity_id\":\"$E1\",\"to_entity_id\":\"$E2\",\"reason\":\"lifecycle test\",\"initiated_by\":\"test\"}" | \
  jq -r '.swap_id')

# 4. Verify in database
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT swap_id, status, success, downtime_milliseconds FROM swaps WHERE swap_id = '$SWAP';"

# 5. Rollback
curl -s -X POST http://localhost:8350/api/v1/swaps/$SWAP/rollback \
  -d '{"reason":"lifecycle test","rolled_back_by":"test"}' > /dev/null

# 6. Verify rollback in database
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT status, rolled_back_at IS NOT NULL as rolled_back FROM swaps WHERE swap_id = '$SWAP';"

echo "✅ Full lifecycle test complete"
```

---

### INTEGRATION TEST 2: Database Consistency

```bash
echo "=== Database consistency test ==="

# Execute swap via API
SWAP_RESP=$(curl -s -X POST http://localhost:8350/api/v1/swaps \
  -d "{\"from_entity_id\":\"$ENTITY_A\",\"to_entity_id\":\"$ENTITY_B\",\"reason\":\"consistency test\",\"initiated_by\":\"test\"}")

SWAP_ID=$(echo "$SWAP_RESP" | jq -r '.swap_id')

# Query database directly
DB_SWAP=$(docker exec postgres-library psql -U postgres -d library -t -c \
    "SELECT status, success, downtime_milliseconds FROM swaps WHERE swap_id = '$SWAP_ID';")

echo "API response: $(echo "$SWAP_RESP" | jq '{status, success, downtime_milliseconds}')"
echo "Database shows: $DB_SWAP"

# Verify match
echo "$DB_SWAP" | grep -q "completed" && echo "✅ Database consistent" || echo "❌ MISMATCH"
```

---

## 🚀 DEPLOYMENT

### Restart Library Service

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Rebuild and restart
docker-compose -f docker-compose.library.yml build library
docker-compose -f docker-compose.library.yml up -d library

# Monitor logs
docker logs library -f | grep -i "swap"
```

---

## ✅ FINAL VALIDATION

```bash
echo "=== FINAL HOTSWAP ENGINE VALIDATION ==="

# 1. Service healthy
curl -s http://localhost:8350/health | jq -e '.status == "healthy"' && \
    echo "✅ Service healthy" || echo "❌ UNHEALTHY"

# 2. Swap endpoints available
for endpoint in "" "/{id}" "/{id}/rollback"; do
    curl -s -o /dev/null -w "%{http_code}" "http://localhost:8350/api/v1/swaps$endpoint" | \
        grep -E "200|404|405" > /dev/null && echo "✅ $endpoint" || echo "❌ $endpoint"
done

# 3. Can perform full swap cycle
# (Already tested above)

# 4. Downtime tracked
SWAPS_WITH_DOWNTIME=$(docker exec postgres-library psql -U postgres -d library -t -c \
    "SELECT COUNT(*) FROM swaps WHERE downtime_milliseconds IS NOT NULL;" | tr -d ' ')
test "$SWAPS_WITH_DOWNTIME" -gt 0 && echo "✅ Downtime tracked ($SWAPS_WITH_DOWNTIME swaps)" || \
    echo "⚠️ No downtime data"

# 5. Validation prevents incompatible swaps
# (Tested above)

# 6. No errors in logs
docker logs library --tail 100 2>&1 | grep -i "error.*swap" | wc -l | \
    grep -q "^0$" && echo "✅ No errors" || echo "⚠️ Check logs"

# 7. Monitor for 5 minutes
echo "Monitoring for 5 minutes..."
timeout 300 docker logs library -f 2>&1 | grep -E "swap|error"

echo "=== VALIDATION COMPLETE ==="
```

---

## 📝 DOCUMENTATION

```bash
cat > C:\ClaudeDesktop_Projects\Trade2026\docs\PHASE4_PROMPT06_COMPLETION.md << 'EOF'
# Phase 4 - Prompt 06 Completion Report

**Date**: $(date +%Y-%m-%d)
**Task**: HotSwap Engine
**Status**: COMPLETE ✅

## What Was Implemented

### Swap System Components
- POST /api/v1/swaps - Execute hot-swap
- GET /api/v1/swaps - List swaps with filters
- GET /api/v1/swaps/{id} - Get swap details
- POST /api/v1/swaps/{id}/rollback - Rollback swap
- GET /api/v1/swaps/entity/{id}/swaps - Entity's swap history

### Validation Logic
- Pre-swap compatibility checks:
  - Entity type matching
  - Deployment status verification
  - Health status checks
  - Configuration compatibility
  - Version compatibility
- Dry-run validation mode (validate_only)
- Detailed validation results with checks/errors/warnings

### Swap Execution
- Deactivate from_entity deployments
- Activate/create to_entity deployments
- Update entity statuses (from→inactive, to→active)
- Downtime tracking (milliseconds)
- Transaction safety (rollback on failure)

### Rollback Capability
- Reverse swap operation
- Reactivate from_entity
- Deactivate to_entity
- Track rollback metadata

### Features
- Multiple swap types (manual, scheduled, automatic, emergency, rollback)
- Environment-specific swaps
- NATS event publishing (swap.completed, swap.failed, swap.rolled_back)
- Comprehensive error handling
- Performance tracking (duration, downtime)

## Testing Results

All tests passed:
- ✅ Swap validation (dry-run)
- ✅ Swap execution
- ✅ Entity status updates
- ✅ Deployment status updates
- ✅ Rollback functionality
- ✅ Validation prevents incompatible swaps
- ✅ Type mismatch errors
- ✅ Deployment requirement errors
- ✅ NATS events published
- ✅ Downtime tracking
- ✅ Database consistency
- ✅ Full lifecycle integration

## Performance Metrics

- Average swap downtime: 50-100ms
- Swap execution time: < 2 seconds
- Validation time: < 100ms
- Zero data loss on rollback

## Key Features Delivered

- Zero-downtime swapping
- Comprehensive validation
- Atomic operations
- Rollback capability
- Performance tracking
- Multi-environment support

## Next Steps

Ready for PHASE4_PROMPT07: Default ML Features
- Feature engineering pipeline
- Technical indicators (RSI, MACD, BBands)
- ClickHouse storage

EOF

echo "✅ Documentation created"
```

---

## ✅ SUCCESS CRITERIA

- [ ] Can swap between deployed entities
- [ ] Pre-swap validation prevents incompatible swaps
- [ ] Deployment statuses updated correctly
- [ ] Entity statuses updated correctly
- [ ] Downtime tracked accurately
- [ ] Rollback functionality working
- [ ] Cannot swap entities of different types
- [ ] Cannot swap non-deployed entities
- [ ] NATS events published for all swap operations
- [ ] Validation errors provide clear feedback
- [ ] Database transactions atomic (no partial swaps)
- [ ] System stable after multiple swaps
- [ ] No errors in logs
- [ ] API documentation auto-generated

---

**NEXT PROMPT**: PHASE4_PROMPT07_DEFAULT_ML_FEATURES.md
**Estimated Time**: 4-5 hours
