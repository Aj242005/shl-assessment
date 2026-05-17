from dataclasses import dataclass, field

KEY_TO_CODE = {
    "Ability & Aptitude": "A",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Assessment Exercises": "E",
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S"
}

@dataclass
class Assessment:
    entity_id: str
    name: str
    link: str
    job_levels: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    duration: str = ""
    description: str = ""
    keys: list[str] = field(default_factory=list)
    remote: str = "yes"
    adaptive: str = "no"

    @property
    def test_type_codes(self) -> str:
        codes = [KEY_TO_CODE.get(key) for key in self.keys]
        codes = [c for c in codes if c is not None]
        return ",".join(codes)

    def to_context_string(self) -> str:
        context = f"Name: {self.name}\n"
        context += f"Description: {self.description}\n"
        if self.duration:
            context += f"Duration: {self.duration}\n"
        if self.languages:
            context += f"Languages: {', '.join(self.languages)}\n"
        if self.job_levels:
            context += f"Target Job Levels: {', '.join(self.job_levels)}\n"
        if self.keys:
            context += f"Categories: {', '.join(self.keys)}\n"
        context += f"URL: {self.link}\n"
        context += f"Test Type Code: {self.test_type_codes}\n"
        return context
