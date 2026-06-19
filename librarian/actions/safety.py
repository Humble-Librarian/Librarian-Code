from enum import Enum


class RiskLevel(Enum):
    SAFE = "safe"
    CONFIRM = "confirm"


CONFIRM_ACTIONS = [
    "git push",
    "git reset --hard",
    "rm ",
    "delete",
    "drop table",
    "truncate",
]


def classify_action(action: str) -> RiskLevel:
    action_lower = action.lower()
    for pattern in CONFIRM_ACTIONS:
        if pattern in action_lower:
            return RiskLevel.CONFIRM
    return RiskLevel.SAFE


def request_confirm(action: str) -> bool:
    from rich.prompt import Confirm
    return Confirm.ask(f"[bold #F59E0B]confirm:[/bold #F59E0B] {action}")
