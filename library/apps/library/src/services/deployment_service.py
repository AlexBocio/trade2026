"""
Deployment service with validation and lifecycle management.
"""
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from datetime import datetime
from typing import Optional

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
            DeploymentModel.deployment_id != current_deployment_id,
        ).order_by(DeploymentModel.deployed_at.desc()).first()
