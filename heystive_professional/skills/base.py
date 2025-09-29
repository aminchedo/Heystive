class Skill:
    name: str = "skill"
    def can_handle(self, text: str) -> bool:
        return False
    def handle(self, text: str, context: dict) -> dict:
        return {}