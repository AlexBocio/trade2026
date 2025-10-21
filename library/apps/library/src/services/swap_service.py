"""
Swap service with validation and lifecycle management.
"""
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from datetime import datetime
from typing import Optional, Tuple
import time

from ..db.models import Entity as EntityModel, Deployment as DeploymentModel, Swap as SwapModel
from ..schemas.swap import SwapValidation, SwapStatus

logger = logging.getLogger(__name__)


class SwapService:
    """Service for swap operations."""

    @staticmethod
    def validate_swap_compatibility(
        from_entity_id: UUID,
        to_entity_id: UUID,
        environment: str,
        db: Session
    ) -> SwapValidation:
        """
        Validate that two entities can be swapped.

        Checks:
        - Both entities exist and not deleted
        - Both entities are same type (strategy->strategy, pipeline->pipeline)
        - From entity has active deployment in target environment
        - To entity is ready for deployment
        - No circular dependencies would be created
        - Configuration compatibility
        """
        errors = []
        warnings = []
        checks = {}

        # Check 1: From entity exists and not deleted
        from_entity = db.query(EntityModel).filter(
            EntityModel.entity_id == from_entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not from_entity:
            errors.append(f"From entity {from_entity_id} not found or deleted")
            checks['from_entity_exists'] = False
        else:
            checks['from_entity_exists'] = True

        # Check 2: To entity exists and not deleted
        to_entity = db.query(EntityModel).filter(
            EntityModel.entity_id == to_entity_id,
            EntityModel.deleted_at.is_(None)
        ).first()

        if not to_entity:
            errors.append(f"To entity {to_entity_id} not found or deleted")
            checks['to_entity_exists'] = False
        else:
            checks['to_entity_exists'] = True

        # If either entity doesn't exist, can't continue validation
        if not from_entity or not to_entity:
            return SwapValidation(
                passed=False,
                checks=checks,
                errors=errors,
                warnings=warnings,
                can_proceed=False
            )

        # Check 3: Entity types must match
        if from_entity.type != to_entity.type:
            errors.append(
                f"Entity type mismatch: {from_entity.type} != {to_entity.type}. "
                f"Can only swap entities of same type."
            )
            checks['entity_types_match'] = False
        else:
            checks['entity_types_match'] = True

        # Check 4: From entity must have active deployment in environment
        from_deployment = db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == from_entity_id,
            DeploymentModel.environment == environment,
            DeploymentModel.status == 'active'
        ).first()

        if not from_deployment:
            errors.append(
                f"From entity {from_entity.name} has no active deployment in {environment}"
            )
            checks['from_entity_deployed'] = False
        else:
            checks['from_entity_deployed'] = True
            checks['from_deployment_id'] = str(from_deployment.deployment_id)

        # Check 5: To entity status must be deployable
        if to_entity.status not in ['registered', 'validated', 'deployed', 'active']:
            errors.append(
                f"To entity {to_entity.name} status '{to_entity.status}' not deployable"
            )
            checks['to_entity_ready'] = False
        else:
            checks['to_entity_ready'] = True

        # Check 6: To entity health must not be unhealthy
        if to_entity.health_status == 'unhealthy':
            errors.append(f"To entity {to_entity.name} health is unhealthy")
            checks['to_entity_healthy'] = False
        else:
            checks['to_entity_healthy'] = True

        # Check 7: Check if to_entity already deployed in same environment
        to_existing_deployment = db.query(DeploymentModel).filter(
            DeploymentModel.entity_id == to_entity_id,
            DeploymentModel.environment == environment,
            DeploymentModel.status == 'active'
        ).first()

        if to_existing_deployment:
            warnings.append(
                f"To entity {to_entity.name} already has active deployment in {environment}. "
                f"This deployment will be reused for the swap."
            )
            checks['to_entity_already_deployed'] = True
        else:
            checks['to_entity_already_deployed'] = False

        # Check 8: Version comparison
        if from_entity.version and to_entity.version:
            checks['from_version'] = from_entity.version
            checks['to_version'] = to_entity.version
            if from_entity.version == to_entity.version:
                warnings.append(
                    f"Both entities have same version '{from_entity.version}'. "
                    f"Consider versioning if this is an upgrade."
                )

        # Check 9: Category match (warning only)
        if from_entity.category != to_entity.category:
            warnings.append(
                f"Category mismatch: {from_entity.category} -> {to_entity.category}"
            )
            checks['categories_match'] = False
        else:
            checks['categories_match'] = True

        # Check 10: Dependencies validation
        if to_entity.requirements:
            from ..services.dependency_service import DependencyService
            dep_validation = DependencyService.validate_dependencies(to_entity_id, db)
            if not dep_validation['valid']:
                for error in dep_validation['errors']:
                    errors.append(f"Dependency error: {error}")
            for warning in dep_validation['warnings']:
                warnings.append(f"Dependency warning: {warning}")
            checks['dependencies_valid'] = dep_validation['valid']
        else:
            checks['dependencies_valid'] = True

        # Determine if swap can proceed
        passed = len(errors) == 0
        can_proceed = passed

        return SwapValidation(
            passed=passed,
            checks=checks,
            errors=errors,
            warnings=warnings,
            can_proceed=can_proceed
        )

    @staticmethod
    def execute_swap(
        swap: SwapModel,
        config_override: Optional[dict],
        parameters_override: Optional[dict],
        db: Session
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute a swap operation.

        Process:
        1. Get from and to entities
        2. Get from deployment (active in environment)
        3. Create or reuse to deployment
        4. Deactivate from deployment
        5. Activate to deployment
        6. Update entity statuses
        7. Track downtime

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        start_time = time.time()
        execution_logs = []

        try:
            # Get entities
            from_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == swap.from_entity_id
            ).first()
            to_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == swap.to_entity_id
            ).first()

            if not from_entity or not to_entity:
                return False, "Entity not found during swap execution"

            execution_logs.append(f"Starting swap: {from_entity.name} -> {to_entity.name}")

            # Get from deployment
            from_deployment = db.query(DeploymentModel).filter(
                DeploymentModel.entity_id == swap.from_entity_id,
                DeploymentModel.environment == swap.environment,
                DeploymentModel.status == 'active'
            ).first()

            if not from_deployment:
                return False, f"No active deployment found for {from_entity.name} in {swap.environment}"

            execution_logs.append(f"Found from deployment: {from_deployment.deployment_id}")
            swap.from_deployment_id = from_deployment.deployment_id

            # Check if to_entity already has deployment in environment
            to_deployment = db.query(DeploymentModel).filter(
                DeploymentModel.entity_id == swap.to_entity_id,
                DeploymentModel.environment == swap.environment,
                DeploymentModel.status == 'active'
            ).first()

            if to_deployment:
                # Reuse existing deployment
                execution_logs.append(f"Reusing existing deployment: {to_deployment.deployment_id}")
                swap.to_deployment_id = to_deployment.deployment_id
            else:
                # Create new deployment for to_entity
                config_snapshot = config_override if config_override else to_entity.config
                params_snapshot = parameters_override if parameters_override else to_entity.parameters

                to_deployment = DeploymentModel(
                    entity_id=to_entity.entity_id,
                    version=to_entity.version,
                    environment=swap.environment,
                    config_snapshot=config_snapshot,
                    parameters_snapshot=params_snapshot,
                    status='active',
                    deployed_by=swap.initiated_by,
                    deployment_method='hotswap'
                )
                db.add(to_deployment)
                db.flush()  # Get deployment_id

                execution_logs.append(f"Created new deployment: {to_deployment.deployment_id}")
                swap.to_deployment_id = to_deployment.deployment_id

            # Record swap config snapshot
            swap.config_snapshot = to_deployment.config_snapshot

            # Deactivate from deployment
            from_deployment.status = 'inactive'
            execution_logs.append(f"Deactivated from deployment")

            # Update from entity status
            from_entity.status = 'inactive'
            execution_logs.append(f"Set {from_entity.name} status to inactive")

            # Update to entity status
            to_entity.status = 'active'
            to_entity.deployed_at = datetime.utcnow()
            to_entity.deployed_by = swap.initiated_by
            to_entity.deployment_config = to_deployment.config_snapshot
            execution_logs.append(f"Set {to_entity.name} status to active")

            # Calculate downtime in milliseconds
            end_time = time.time()
            downtime_ms = int((end_time - start_time) * 1000)
            swap.downtime_milliseconds = downtime_ms
            execution_logs.append(f"Swap completed in {downtime_ms}ms")

            # Update swap status
            swap.status = SwapStatus.COMPLETED
            swap.completed_at = datetime.utcnow()
            swap.execution_logs = execution_logs

            db.flush()

            logger.info(
                f"Swap completed: {from_entity.name} -> {to_entity.name} "
                f"in {swap.environment} ({downtime_ms}ms downtime)"
            )

            return True, None

        except Exception as e:
            error_msg = f"Swap execution failed: {str(e)}"
            logger.error(error_msg)
            execution_logs.append(error_msg)

            swap.status = SwapStatus.FAILED
            swap.failed_at = datetime.utcnow()
            swap.error_message = error_msg
            swap.execution_logs = execution_logs

            db.flush()

            return False, error_msg

    @staticmethod
    def rollback_swap(
        swap: SwapModel,
        rolled_back_by: str,
        reason: Optional[str],
        db: Session
    ) -> Tuple[bool, Optional[str]]:
        """
        Rollback a swap operation.

        Process:
        1. Verify swap is completed (can't rollback failed/pending swaps)
        2. Reactivate from deployment
        3. Deactivate to deployment
        4. Update entity statuses
        5. Update swap record

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Verify swap can be rolled back
            if swap.status != SwapStatus.COMPLETED:
                return False, f"Cannot rollback swap with status '{swap.status}'. Only completed swaps can be rolled back."

            if not swap.from_deployment_id or not swap.to_deployment_id:
                return False, "Cannot rollback: missing deployment references"

            # Get deployments
            from_deployment = db.query(DeploymentModel).filter(
                DeploymentModel.deployment_id == swap.from_deployment_id
            ).first()

            to_deployment = db.query(DeploymentModel).filter(
                DeploymentModel.deployment_id == swap.to_deployment_id
            ).first()

            if not from_deployment or not to_deployment:
                return False, "Cannot rollback: deployment not found"

            # Get entities
            from_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == swap.from_entity_id
            ).first()

            to_entity = db.query(EntityModel).filter(
                EntityModel.entity_id == swap.to_entity_id
            ).first()

            if not from_entity or not to_entity:
                return False, "Cannot rollback: entity not found"

            # Reactivate from deployment
            from_deployment.status = 'active'

            # Deactivate to deployment
            to_deployment.status = 'inactive'

            # Update from entity status
            from_entity.status = 'active'
            from_entity.deployed_at = datetime.utcnow()
            from_entity.deployed_by = rolled_back_by
            from_entity.deployment_config = from_deployment.config_snapshot

            # Update to entity status
            to_entity.status = 'inactive'

            # Update swap record
            swap.status = SwapStatus.ROLLED_BACK
            swap.rolled_back_at = datetime.utcnow()
            swap.rolled_back_by = rolled_back_by
            swap.rollback_reason = reason

            db.flush()

            logger.info(
                f"Swap rolled back: {swap.swap_id} by {rolled_back_by}. "
                f"Restored {from_entity.name} in {swap.environment}"
            )

            return True, None

        except Exception as e:
            error_msg = f"Swap rollback failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def get_active_swap_in_environment(
        entity_id: UUID,
        environment: str,
        db: Session
    ) -> Optional[SwapModel]:
        """
        Get any active/in-progress swap for an entity in an environment.

        This prevents concurrent swaps.
        """
        return db.query(SwapModel).filter(
            SwapModel.environment == environment,
            SwapModel.status.in_([SwapStatus.PENDING, SwapStatus.IN_PROGRESS]),
            (SwapModel.from_entity_id == entity_id) | (SwapModel.to_entity_id == entity_id)
        ).first()
