from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker
from src.checkmate.violation_checkers.CallgraphViolationChecker import CallgraphViolationChecker


def get_violation_checker_for_task(task: str, jobs: int, groundtruths, reader) -> AbstractViolationChecker:
    if task.lower() == "cg":
        return CallgraphViolationChecker(jobs, groundtruths, reader)