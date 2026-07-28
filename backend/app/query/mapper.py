from llama_index.core.base.response.schema import Response

from app.query.schemas import QueryResponse, QuerySource


def to_query_response(response: Response) -> QueryResponse:
    answer = response.response

    if answer is None:
        answer = ""
    elif not isinstance(answer, str):
        answer = str(answer)

    return QueryResponse(
        answer=answer,
        sources=[
            QuerySource(
                text=node.node.text, # type: ignore
                score=node.score or 0.0,
                filename=node.node.metadata.get("filename", "Unknown"),
                page_number=node.node.metadata.get("page_number", 0),
            )
            for node in response.source_nodes
        ],
    )