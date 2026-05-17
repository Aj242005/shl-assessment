import json
import logging
from typing import Optional
from app.assessment import Assessment
from app.config import settings

logger = logging.getLogger(__name__)

class CatalogStore:
    def __init__(self):
        self.assessments: list[Assessment] = []
        self.name_index: dict[str, Assessment] = {}
        self.id_index: dict[str, Assessment] = {}
        self.url_index: dict[str, Assessment] = {}
        self._load_catalog()

    def _load_catalog(self):
        try:
            with open(settings.CATALOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f, strict=False)

            for item in data:
                assessment = Assessment(
                    entity_id=item.get("entity_id", ""),
                    name=item.get("name", ""),
                    link=item.get("link", ""),
                    job_levels=item.get("job_levels", []),
                    languages=item.get("languages", []),
                    duration=item.get("duration", ""),
                    description=item.get("description", ""),
                    keys=item.get("keys", []),
                    remote=item.get("remote", "yes"),
                    adaptive=item.get("adaptive", "no")
                )
                self.assessments.append(assessment)

                if assessment.name:
                    self.name_index[assessment.name.lower()] = assessment
                if assessment.entity_id:
                    self.id_index[assessment.entity_id] = assessment
                if assessment.link:
                    self.url_index[assessment.link] = assessment

            logger.info(f"Loaded {len(self.assessments)} assessments from catalog.")
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
            raise

    def get_all(self) -> list[Assessment]:
        return self.assessments

    def get_by_name(self, name: str) -> Assessment | None:
        return self.name_index.get(name.lower())

    def get_by_url(self, url: str) -> Assessment | None:
        return self.url_index.get(url)

    def validate_url(self, url: str) -> bool:
        return url in self.url_index
