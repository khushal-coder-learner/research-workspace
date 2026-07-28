from types import SimpleNamespace

from app.query.mapper import to_query_response


def test_to_query_response_maps_answer_and_sources() -> None:
    # Arrange
    response = SimpleNamespace(
        response="The answer",
        source_nodes=[
            SimpleNamespace(
                node=SimpleNamespace(
                    text="Source text", metadata={"filename": "paper.pdf", "page_number": 3}
                ),
                score=0.8,
            )
        ],
    )

    # Act
    result = to_query_response(response)

    # Assert
    assert result.answer == "The answer"
    assert len(result.sources) == 1
    assert result.sources[0].text == "Source text"
    assert result.sources[0].score == 0.8
    assert result.sources[0].filename == "paper.pdf"
    assert result.sources[0].page_number == 3


def test_to_query_response_defaults_missing_answer_and_source_metadata() -> None:
    # Arrange
    response = SimpleNamespace(
        response=None,
        source_nodes=[
            SimpleNamespace(
                node=SimpleNamespace(text="Source text", metadata={}),
                score=None,
            )
        ],
    )

    # Act
    result = to_query_response(response)

    # Assert
    assert result.answer == ""
    assert result.sources[0].score == 0.0
    assert result.sources[0].filename == "Unknown"
    assert result.sources[0].page_number == 0


def test_to_query_response_converts_non_string_answer_and_supports_no_sources() -> None:
    # Arrange
    response = SimpleNamespace(response=123, source_nodes=[])

    # Act
    result = to_query_response(response)

    # Assert
    assert result.answer == "123"
    assert result.sources == []
