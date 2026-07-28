from uuid import UUID

from llama_index.core.vector_stores import MetadataFilter, MetadataFilters


def project_filter(project_id: UUID) -> MetadataFilters:
    """Create a metadata filter for a project."""
    return MetadataFilters(
        filters=[
            MetadataFilter(
                key="project_id",
                value=str(project_id),
            )
        ]
    )