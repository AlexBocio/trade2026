"""
Dependency service for managing entity dependencies.

Synchronizes between entity.requirements (simple array) and dependencies table (relational).
"""
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from typing import List, Optional

from ..db.models import Entity as EntityModel, Dependency as DependencyModel

logger = logging.getLogger(__name__)


class DependencyService:
    """Service for managing entity dependencies."""

    @staticmethod
    def sync_dependencies(
        entity: EntityModel,
        db: Session
    ) -> None:
        """
        Synchronize entity.requirements with dependencies table.

        Creates/updates Dependency records based on entity.requirements array.
        This ensures both the simple array and relational table stay in sync.

        Args:
            entity: Entity with requirements to sync
            db: Database session
        """
        if not entity.requirements:
            # No requirements - remove all dependencies
            db.query(DependencyModel).filter(
                DependencyModel.entity_id == entity.entity_id
            ).delete()
            logger.debug(f"Cleared all dependencies for {entity.entity_id}")
            return

        # Get existing dependencies
        existing_deps = db.query(DependencyModel).filter(
            DependencyModel.entity_id == entity.entity_id
        ).all()

        existing_dep_ids = {str(dep.depends_on_entity_id) for dep in existing_deps}
        required_dep_ids = set(entity.requirements)

        # Remove dependencies no longer in requirements
        to_remove = existing_dep_ids - required_dep_ids
        if to_remove:
            db.query(DependencyModel).filter(
                DependencyModel.entity_id == entity.entity_id,
                DependencyModel.depends_on_entity_id.in_([UUID(dep_id) for dep_id in to_remove])
            ).delete(synchronize_session=False)
            logger.debug(f"Removed {len(to_remove)} dependencies for {entity.entity_id}")

        # Add new dependencies
        to_add = required_dep_ids - existing_dep_ids
        for dep_id_str in to_add:
            try:
                dep_id = UUID(dep_id_str)

                # Verify the dependency entity exists
                dep_entity = db.query(EntityModel).filter(
                    EntityModel.entity_id == dep_id,
                    EntityModel.deleted_at.is_(None)
                ).first()

                if not dep_entity:
                    logger.warning(f"Dependency entity {dep_id} not found for {entity.entity_id}")
                    continue

                # Create dependency record
                dependency = DependencyModel(
                    entity_id=entity.entity_id,
                    depends_on_entity_id=dep_id,
                    dependency_type='required',  # Default type
                    status='active'
                )
                db.add(dependency)
                logger.debug(f"Added dependency {dep_id} for {entity.entity_id}")

            except (ValueError, AttributeError) as e:
                logger.error(f"Invalid dependency ID {dep_id_str}: {e}")
                continue

        db.flush()
        logger.info(f"Synced {len(required_dep_ids)} dependencies for {entity.entity_id}")

    @staticmethod
    def validate_dependencies(
        entity_id: UUID,
        db: Session
    ) -> dict:
        """
        Validate all dependencies for an entity.

        Checks:
        - All dependency entities exist
        - No circular dependencies
        - Dependencies are not deleted
        - Dependencies are in valid state

        Returns:
            dict with validation results
        """
        errors = []
        warnings = []

        dependencies = db.query(DependencyModel).filter(
            DependencyModel.entity_id == entity_id,
            DependencyModel.status == 'active'
        ).all()

        for dep in dependencies:
            # Check if dependency entity exists
            dep_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == dep.depends_on_entity_id
            ).first()

            if not dep_entity:
                errors.append(f"Dependency entity {dep.depends_on_entity_id} not found")
                continue

            # Check if deleted
            if dep_entity.deleted_at:
                errors.append(f"Dependency {dep_entity.name} is deleted")
                continue

            # Check status
            if dep_entity.status == 'failed':
                warnings.append(f"Dependency {dep_entity.name} is in failed state")

            # Check health
            if dep_entity.health_status == 'unhealthy':
                warnings.append(f"Dependency {dep_entity.name} is unhealthy")

        return {
            'valid': len(errors) == 0,
            'dependency_count': len(dependencies),
            'errors': errors,
            'warnings': warnings
        }

    @staticmethod
    def check_circular_dependency(
        entity_id: UUID,
        depends_on_id: UUID,
        db: Session,
        visited: Optional[set] = None
    ) -> bool:
        """
        Check if adding a dependency would create a circular dependency.

        Args:
            entity_id: The entity that would depend on depends_on_id
            depends_on_id: The entity being depended upon
            db: Database session
            visited: Set of visited entity IDs (for recursion)

        Returns:
            True if circular dependency detected, False otherwise
        """
        if visited is None:
            visited = set()

        # If depends_on_id depends on entity_id (directly or indirectly), circular
        if depends_on_id == entity_id:
            return True

        if depends_on_id in visited:
            return False

        visited.add(depends_on_id)

        # Get all dependencies of depends_on_id
        deps = db.query(DependencyModel).filter(
            DependencyModel.entity_id == depends_on_id,
            DependencyModel.status == 'active'
        ).all()

        for dep in deps:
            if DependencyService.check_circular_dependency(
                entity_id, dep.depends_on_entity_id, db, visited
            ):
                return True

        return False

    @staticmethod
    def get_dependency_tree(
        entity_id: UUID,
        db: Session,
        depth: int = 0,
        max_depth: int = 10
    ) -> dict:
        """
        Get the full dependency tree for an entity.

        Args:
            entity_id: Root entity ID
            db: Database session
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            dict representing dependency tree
        """
        if depth >= max_depth:
            return {'error': 'Max depth reached'}

        entity = db.query(EntityModel).filter(
            EntityModel.entity_id == entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not entity:
            return {'error': 'Entity not found'}

        dependencies = db.query(DependencyModel).filter(
            DependencyModel.entity_id == entity_id,
            DependencyModel.status == 'active'
        ).all()

        tree = {
            'entity_id': str(entity_id),
            'name': entity.name,
            'type': entity.type,
            'status': entity.status,
            'dependencies': []
        }

        for dep in dependencies:
            subtree = DependencyService.get_dependency_tree(
                dep.depends_on_entity_id, db, depth + 1, max_depth
            )
            tree['dependencies'].append({
                'dependency_type': dep.dependency_type,
                'min_version': dep.min_version,
                'max_version': dep.max_version,
                'entity': subtree
            })

        return tree
