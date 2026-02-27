from app.models.rag_models import IngestionConfig, IngestionStats


class IngestionPipeline:
    def __init__(self, config: IngestionConfig):
        """Initialize pipeline with configuration."""
        pass

    def ingest_file(self, file_path: str, clear_existing: bool = False) -> IngestionStats:
        """Process WhatsApp export file and index it."""
        pass

    def _show_progress(self, current: int, total: int, stage: str) -> None:
        """Display progress bar."""
        pass