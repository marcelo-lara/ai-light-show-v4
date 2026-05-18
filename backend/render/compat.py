from pydantic import ValidationError

from render.artifact import ArtifactMetaV1

SUPPORTED_SCHEMA_VERSIONS = {1}


class CompatibilityError(ValueError):
    pass


def check_artifact_compat(raw: dict) -> ArtifactMetaV1:
    version = raw.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise CompatibilityError(
            f"Unsupported schema_version={version!r}. "
            f"Supported: {SUPPORTED_SCHEMA_VERSIONS}"
        )
    try:
        return ArtifactMetaV1.model_validate(raw)
    except ValidationError as exc:
        raise CompatibilityError(f"Invalid artifact: {exc}") from exc
