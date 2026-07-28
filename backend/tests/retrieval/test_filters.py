from uuid import UUID

from app.retrieval.filters import project_filter


def test_project_filter_scopes_results_to_project() -> None:
    # Arrange
    project_id = UUID("22222222-2222-2222-2222-222222222222")

    # Act
    filters = project_filter(project_id)

    # Assert
    assert len(filters.filters) == 1
    assert filters.filters[0].key == "project_id"
    assert filters.filters[0].value == str(project_id)
