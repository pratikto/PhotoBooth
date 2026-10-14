"""Small, testable models for order sessions and customer retakes."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from photobooth.catalog import BoothTemplate


@dataclass(frozen=True)
class SessionPlan:
    """The template and order position assigned to one independent photo session."""

    session_id: str
    template: BoothTemplate
    order_number: int
    total_sessions: int
    template_session_number: int
    template_session_count: int


@dataclass
class PhotoSession:
    """Mutable photo state for one session, including its own retake allowance."""

    plan: SessionPlan
    initial_photo_paths: list[Path] = field(default_factory=list)
    selected_index: int | None = None
    retake_path: Path | None = None
    retake_target_index: int | None = None
    output_path: Path | None = None

    @property
    def ready_for_review(self) -> bool:
        return len(self.initial_photo_paths) == 3

    @property
    def retake_used(self) -> bool:
        return self.retake_path is not None

    @property
    def can_retake(self) -> bool:
        return (
            self.ready_for_review
            and self.selected_index is not None
            and not self.retake_used
        )

    @property
    def raw_photo_paths(self) -> list[Path]:
        paths = list(self.initial_photo_paths)
        if self.retake_path is not None:
            paths.append(self.retake_path)
        return paths

    @property
    def final_photo_paths(self) -> list[Path]:
        photos = list(self.initial_photo_paths)
        if self.retake_path is not None and self.retake_target_index is not None:
            photos[self.retake_target_index] = self.retake_path
        return photos

    def add_initial_photo(self, path: Path) -> None:
        if len(self.initial_photo_paths) >= 3:
            raise ValueError("This session already has three initial photos.")
        self.initial_photo_paths.append(Path(path))

    def select_photo(self, index: int) -> None:
        if not self.ready_for_review:
            raise ValueError("Capture all three photos before selecting one.")
        if index < 0 or index >= 3:
            raise IndexError("Photo selection must be between 0 and 2.")
        self.selected_index = index

    def apply_retake(self, path: Path) -> None:
        if self.selected_index is None:
            raise ValueError("Select one photo before using the retake.")
        if self.retake_used:
            raise ValueError("The retake for this session has already been used.")
        self.retake_path = Path(path)
        self.retake_target_index = self.selected_index


def build_session_plans(
    templates: Sequence[BoothTemplate],
    quantities: Mapping[str, int],
) -> list[SessionPlan]:
    """Expand template quantities into ordered, independent photo sessions."""
    template_counts: dict[str, int] = {}
    for template in templates:
        quantity = quantities.get(template.template_id, 0)
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Template quantities must be non-negative integers.")
        template_counts[template.template_id] = quantity

    total = sum(template_counts.values())
    plans: list[SessionPlan] = []
    order_number = 0

    for template in templates:
        quantity = template_counts[template.template_id]
        for template_session_number in range(1, quantity + 1):
            order_number += 1
            plans.append(
                SessionPlan(
                    session_id=f"session_{order_number:03d}",
                    template=template,
                    order_number=order_number,
                    total_sessions=total,
                    template_session_number=template_session_number,
                    template_session_count=quantity,
                )
            )

    return plans
