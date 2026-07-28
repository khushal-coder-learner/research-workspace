from llama_index.core.node_parser import SentenceSplitter
from app.core.config import settings

parser = SentenceSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)