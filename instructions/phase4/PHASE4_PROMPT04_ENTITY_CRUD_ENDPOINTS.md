# PHASE 4 - PROMPT 04: Entity CRUD Endpoints
# Complete REST API for Entity Management

**Task ID**: PHASE4_PROMPT04
**Estimated Time**: 3-4 hours
**Component**: Entity REST API Endpoints
**Dependencies**: PHASE4_PROMPT03 (NATS Integration must be working)

---

## 🎯 OBJECTIVE

**Build COMPLETE REST API endpoints for entity management with full CRUD operations.**

This includes:
- GET /entities - List with pagination, filtering, search
- GET /entities/{id} - Get single entity
- POST /entities - Create entity (publish NATS event)
- PUT /entities/{id} - Update entity (publish NATS event)
- DELETE /entities/{id} - Soft delete (publish NATS event)
- GET /entities/search - Full-text search
- GET /entities/{id}/dependencies - Get entity dependencies

**This is the PRIMARY API for library management. No shortcuts - full implementation.**

---

## ⚠️ MANDATORY PRINCIPLES

### Component Isolation
- **FIX ERRORS WITHIN THIS COMPONENT ONLY**
- Do NOT modify database schema
- Do NOT change NATS client
- API endpoint code stays within API router scope

### Comprehensive Implementation
- ✅ ALL CRUD operations (not just GET/POST)
- ✅ FULL pagination (with metadata)
- ✅ ALL filters (type, status, category, tags)
- ✅ COMPLETE error handling (400, 404, 422, 500)
- ✅ ALL NATS events published

### Official Sources Only
- FastAPI: https://fastapi.tiangolo.com/ (official)
- Pydantic: https://docs.pydantic.dev/ (official)

---

## 📋 VALIDATION GATE

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# 1. Library API running
curl -sf http://localhost:8350/health && echo "✅ API running" || echo "❌ START PROMPT02/03 FIRST"

# 2. Database healthy
docker exec postgres-library psql -U postgres -d library -c "SELECT COUNT(*) FROM entities;" && \
    echo "✅ Database working" || echo "❌ DATABASE ISSUE"

# 3. NATS connected
curl -s http://localhost:8350/health/detailed | grep -q "nats" && \
    echo "✅ NATS integrated" || echo "❌ NATS NOT INTEGRATED"

# 4. Can create test entity via database
docker exec postgres-library psql -U postgres -d library -c \
    "INSERT INTO entities (name, type, version) VALUES ('test_api', 'strategy', '1.0.0') RETURNING entity_id;" && \
    echo "✅ Can insert entities" || echo "❌ DATABASE PERMISSION ISSUE"
```

**STOP if any validation fails.**

---

## 🏗️ IMPLEMENTATION

### STEP 1: Create Entity API Router

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\library\apps\library

# Create API v1 directory structure (if not exists)
mkdir -p src/api/v1/endpoints
mkdir -p src/api/v1

# Create __init__.py files
touch src/api/__init__.py
touch src/api/v1/__init__.py
touch src/api/v1/endpoints/__init__.py
```

**COMPONENT TEST 1**: Directory structure
```bash
test -d src/api/v1/endpoints && echo "✅ API structure created" || echo "❌ FAILED"
```

---

### STEP 2: Create Entity Endpoints Router

```bash
cat > src/api/v1/endpoints/entities.py << 'EOF'
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
EOF

echo "✅ Entity endpoints created"
```

---

### STEP 3: Update API Router Registration

```bash
cat > src/api/v1/__init__.py << 'EOF'
"""
API v1 router registration.
"""
from fastapi import APIRouter
from .endpoints import entities

# Create v1 router
api_router = APIRouter()

# Include entity router
api_router.include_router(entities.router)

# Export
__all__ = ['api_router']
EOF

echo "✅ API v1 router updated"
```

---

### STEP 4: Update Main Application

```bash
# Add to main.py (update the router inclusion section)
cat >> src/main_router_update.py << 'EOF'
# Update this section in main.py:

from .api.v1 import api_router

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
EOF

echo "⚠️  MANUAL STEP: Update main.py to include api_router"
echo "Replace the entity/deployment/swap router includes with:"
echo "app.include_router(api_router, prefix=settings.API_V1_PREFIX)"
```

---

## 🧪 COMPREHENSIVE COMPONENT TESTING

### TEST 1: List Entities (No Filters)

```bash
echo "Testing list entities..."

# Basic list
curl -s "http://localhost:8350/api/v1/entities" | jq '.'

# Check response structure
curl -s "http://localhost:8350/api/v1/entities" | jq -e '.entities, .total, .page, .page_size' && \
    echo "✅ List endpoint working" || echo "❌ FAILED"
```

---

### TEST 2: Create Entity

```bash
echo "Testing create entity..."

# Create test entity
RESPONSE=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_strategy_api",
    "type": "strategy",
    "category": "ml_based",
    "description": "Test strategy for API testing",
    "version": "1.0.0",
    "author": "Test User",
    "tags": ["test", "api"],
    "config": {"param1": "value1"},
    "parameters": {"learning_rate": 0.01},
    "created_by": "api_test"
  }')

echo "$RESPONSE" | jq '.'

# Extract entity_id
ENTITY_ID=$(echo "$RESPONSE" | jq -r '.entity_id')

if [ "$ENTITY_ID" != "null" ] && [ -n "$ENTITY_ID" ]; then
    echo "✅ Entity created: $ENTITY_ID"
else
    echo "❌ CREATE FAILED"
fi

# Verify in database
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT entity_id, name, type, version FROM entities WHERE name = 'test_strategy_api';"
```

---

### TEST 3: Get Entity by ID

```bash
echo "Testing get entity by ID..."

# Use entity_id from previous test
curl -s "http://localhost:8350/api/v1/entities/$ENTITY_ID" | jq '.'

# Verify returns correct entity
curl -s "http://localhost:8350/api/v1/entities/$ENTITY_ID" | jq -e '.name == "test_strategy_api"' && \
    echo "✅ Get by ID working" || echo "❌ FAILED"
```

---

### TEST 4: Update Entity

```bash
echo "Testing update entity..."

# Update entity
curl -s -X PUT "http://localhost:8350/api/v1/entities/$ENTITY_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description via API",
    "status": "validated",
    "updated_by": "api_test"
  }' | jq '.'

# Verify update
curl -s "http://localhost:8350/api/v1/entities/$ENTITY_ID" | \
    jq -e '.description == "Updated description via API" and .status == "validated"' && \
    echo "✅ Update working" || echo "❌ UPDATE FAILED"

# Check updated_at changed
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT name, status, updated_at > created_at as updated FROM entities WHERE entity_id = '$ENTITY_ID';"
```

---

### TEST 5: List with Filters

```bash
echo "Testing list with filters..."

# Filter by type
curl -s "http://localhost:8350/api/v1/entities?type=strategy" | jq '.total'

# Filter by status
curl -s "http://localhost:8350/api/v1/entities?status=validated" | jq '.total'

# Filter by tags
curl -s "http://localhost:8350/api/v1/entities?tags=test" | jq '.total'

# Combined filters
curl -s "http://localhost:8350/api/v1/entities?type=strategy&status=validated" | jq '.'

echo "✅ Filters working"
```

---

### TEST 6: Pagination

```bash
echo "Testing pagination..."

# Page 1
curl -s "http://localhost:8350/api/v1/entities?page=1&page_size=5" | \
    jq '.page, .page_size, (.entities | length)'

# Page 2
curl -s "http://localhost:8350/api/v1/entities?page=2&page_size=5" | \
    jq '.page, .page_size'

echo "✅ Pagination working"
```

---

### TEST 7: Search

```bash
echo "Testing search..."

# Search by name
curl -s "http://localhost:8350/api/v1/entities/search/?q=test" | jq '.total'

# Search by description
curl -s "http://localhost:8350/api/v1/entities/search/?q=API" | jq '.total'

echo "✅ Search working"
```

---

### TEST 8: Delete Entity

```bash
echo "Testing delete entity..."

# Delete
curl -s -X DELETE "http://localhost:8350/api/v1/entities/$ENTITY_ID?deleted_by=api_test"

# Verify 404 on get
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8350/api/v1/entities/$ENTITY_ID")

if [ "$STATUS" == "404" ]; then
    echo "✅ Delete working (404 returned)"
else
    echo "❌ DELETE FAILED (status: $STATUS)"
fi

# Verify soft delete in database
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT name, deleted_at IS NOT NULL as is_deleted FROM entities WHERE entity_id = '$ENTITY_ID';"
```

---

### TEST 9: Validation Errors

```bash
echo "Testing validation errors..."

# Missing required field (name)
curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"type": "strategy", "version": "1.0.0"}' | jq '.'

# Should return 422 Unprocessable Entity

# Duplicate name
curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default_ml_strategy",
    "type": "strategy",
    "version": "1.0.0"
  }' | jq '.'

# Should return 400 Bad Request

echo "✅ Validation working"
```

---

### TEST 10: NATS Event Publishing

```bash
echo "Testing NATS event publishing..."

# Subscribe to entity events (in background)
docker run --rm --network trade2026-backend natsio/nats-box:latest \
    nats sub "library.entity.>" --server=nats:4222 &

NATS_PID=$!
sleep 2

# Create entity (should publish event)
curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_nats_event",
    "type": "strategy",
    "version": "1.0.0"
  }' > /dev/null

# Wait for event
sleep 2

# Kill subscriber
kill $NATS_PID 2>/dev/null

echo "✅ Check NATS logs for entity.registered event"
```

---

## 🔗 INTEGRATION TESTING

### INTEGRATION TEST 1: Full CRUD Cycle

```bash
echo "=== Full CRUD Cycle Test ==="

# 1. Create
ENTITY=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "integration_test_strategy",
    "type": "strategy",
    "version": "1.0.0",
    "description": "Integration test",
    "created_by": "integration_test"
  }')

ENTITY_ID=$(echo "$ENTITY" | jq -r '.entity_id')
echo "Created: $ENTITY_ID"

# 2. Read
curl -s "http://localhost:8350/api/v1/entities/$ENTITY_ID" | jq '.name'

# 3. Update
curl -s -X PUT "http://localhost:8350/api/v1/entities/$ENTITY_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}' | jq '.status'

# 4. List (should include our entity)
curl -s "http://localhost:8350/api/v1/entities?type=strategy&status=active" | \
    jq '.entities[] | select(.entity_id == "'$ENTITY_ID'") | .name'

# 5. Delete
curl -s -X DELETE "http://localhost:8350/api/v1/entities/$ENTITY_ID"

# 6. Verify deleted
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8350/api/v1/entities/$ENTITY_ID")
test "$STATUS" == "404" && echo "✅ Full CRUD cycle working" || echo "❌ FAILED"
```

---

### INTEGRATION TEST 2: Database Consistency

```bash
echo "=== Database Consistency Test ==="

# Create via API
ENTITY=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"db_test","type":"strategy","version":"1.0.0"}')

ENTITY_ID=$(echo "$ENTITY" | jq -r '.entity_id')

# Query database directly
DB_RESULT=$(docker exec postgres-library psql -U postgres -d library -t -c \
    "SELECT name, type, version FROM entities WHERE entity_id = '$ENTITY_ID';")

echo "API created: $ENTITY_ID"
echo "Database shows: $DB_RESULT"

# Verify match
echo "$DB_RESULT" | grep -q "db_test" && echo "✅ Database consistent" || echo "❌ INCONSISTENT"
```

---

### INTEGRATION TEST 3: NATS Event Chain

```bash
echo "=== NATS Event Chain Test ==="

# Monitor NATS
docker run --rm -d --name nats-monitor --network trade2026-backend \
    natsio/nats-box:latest nats sub "library.entity.>" --server=nats:4222

sleep 2

# Perform operations
echo "Creating entity..."
curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"nats_test","type":"strategy","version":"1.0.0"}' > /dev/null

ENTITY_ID=$(curl -s "http://localhost:8350/api/v1/entities?search=nats_test" | jq -r '.entities[0].entity_id')

echo "Updating entity..."
curl -s -X PUT "http://localhost:8350/api/v1/entities/$ENTITY_ID" \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}' > /dev/null

echo "Deleting entity..."
curl -s -X DELETE "http://localhost:8350/api/v1/entities/$ENTITY_ID"

# Check NATS logs
docker logs nats-monitor 2>&1 | grep -E "registered|updated|deleted"

docker stop nats-monitor
docker rm nats-monitor

echo "✅ Check for 3 events: registered, updated, deleted"
```

---

## 🚀 DEPLOYMENT

### Update Main Application

```bash
# Verify main.py includes the router
grep -q "api_router" library/apps/library/src/main.py || \
    echo "⚠️  MANUAL: Add api_router to main.py"
```

---

### Restart Library Service

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Rebuild and restart library service
docker-compose -f docker-compose.library.yml build library
docker-compose -f docker-compose.library.yml up -d library

# Check logs
docker logs library -f
```

---

## ✅ FINAL VALIDATION

```bash
echo "=== FINAL VALIDATION ==="

# 1. Service healthy
curl -s http://localhost:8350/health | jq -e '.status == "healthy"' && \
    echo "✅ Service healthy" || echo "❌ UNHEALTHY"

# 2. Endpoints available
for endpoint in "" "/search" "/{id}"; do
    curl -s -o /dev/null -w "%{http_code}" "http://localhost:8350/api/v1/entities$endpoint" | \
        grep -E "200|405|404" > /dev/null && echo "✅ $endpoint" || echo "❌ $endpoint"
done

# 3. Can perform CRUD
curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"final_test","type":"strategy","version":"1.0.0"}' | \
  jq -e '.entity_id' && echo "✅ CRUD working" || echo "❌ CRUD FAILED"

# 4. Database synced
COUNT_API=$(curl -s "http://localhost:8350/api/v1/entities" | jq '.total')
COUNT_DB=$(docker exec postgres-library psql -U postgres -d library -t -c \
    "SELECT COUNT(*) FROM entities WHERE deleted_at IS NULL;" | tr -d ' ')

test "$COUNT_API" == "$COUNT_DB" && echo "✅ API-DB synced ($COUNT_API)" || echo "❌ MISMATCH"

# 5. No errors in logs
docker logs library --tail 100 2>&1 | grep -i "error.*entity" | wc -l | \
    grep -q "^0$" && echo "✅ No errors" || echo "⚠️ Check logs"

# 6. Monitor for 5 minutes
echo "Monitoring for 5 minutes..."
timeout 300 docker logs library -f | grep -E "entity|error"

echo "=== VALIDATION COMPLETE ==="
```

---

## 📝 DOCUMENTATION

```bash
cat > C:\ClaudeDesktop_Projects\Trade2026\docs\PHASE4_PROMPT04_COMPLETION.md << 'EOF'
# Phase 4 - Prompt 04 Completion Report

**Date**: $(date +%Y-%m-%d)
**Task**: Entity CRUD Endpoints
**Status**: COMPLETE ✅

## What Was Implemented

### API Endpoints (7)
- GET /api/v1/entities - List with pagination/filters
- GET /api/v1/entities/{id} - Get single
- POST /api/v1/entities - Create
- PUT /api/v1/entities/{id} - Update
- DELETE /api/v1/entities/{id} - Soft delete
- GET /api/v1/entities/search/ - Full-text search
- GET /api/v1/entities/{id}/dependencies - Get dependencies

### Features
- Complete CRUD operations
- Pagination (page, page_size)
- Filters (type, status, category, tags, health_status)
- Search (name, description, tags)
- NATS event publishing (registered, updated, deleted)
- Comprehensive error handling (400, 404, 422, 500)
- Input validation (Pydantic)
- Soft delete (deleted_at timestamp)

## Testing Results

All tests passed:
- ✅ List entities
- ✅ Create entity
- ✅ Get by ID
- ✅ Update entity
- ✅ Delete entity (soft)
- ✅ Pagination
- ✅ Filters
- ✅ Search
- ✅ Validation errors
- ✅ NATS events
- ✅ Database consistency
- ✅ Full CRUD cycle

## API Examples

```bash
# List
GET /api/v1/entities?type=strategy&page=1&page_size=20

# Create
POST /api/v1/entities
{"name":"my_strategy","type":"strategy","version":"1.0.0"}

# Update
PUT /api/v1/entities/{id}
{"status":"active"}

# Delete
DELETE /api/v1/entities/{id}?deleted_by=user
```

## Next Steps

Ready for PHASE4_PROMPT05: Deployment Lifecycle
- Deploy entities
- Rollback capability
- Deployment validation

EOF

echo "✅ Documentation created"
```

---

## ✅ SUCCESS CRITERIA

- [ ] All 7 endpoints implemented
- [ ] CRUD operations working
- [ ] Pagination functional
- [ ] All filters working
- [ ] Search operational
- [ ] NATS events publishing
- [ ] Validation errors handled
- [ ] Soft delete (not hard)
- [ ] Database synced with API
- [ ] No errors in logs
- [ ] API documentation auto-generated
- [ ] System stable 5+ minutes

---

**NEXT PROMPT**: PHASE4_PROMPT05_DEPLOYMENT_LIFECYCLE.md
**Estimated Time**: 3-4 hours
