# transformations.py

from app.providers.parser import parser
from app.providers.embedding import embedding_model

TRANSFORMATIONS = [
    parser,
    embedding_model,
]