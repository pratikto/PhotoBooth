# PhotoBooth source file
# Small domain models and rules for ordered sessions and per-session retakes.

"""Small, testable models for order sessions and customer retakes."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from photobooth.catalog import BoothTemplate, PRICE_PER_PRINT_COPY, PRICE_PER_SESSION


@dataclass(frozen=True)
class SessionPlan:
    """The template and order position assigned to one independent photo session."""

    session_id: str
    template: BoothTemplate
    order_number: int
    total_sessions: int
    template_session_number: int
    template_session_count: int
    # This session captures exactly three photos once; repeats refer to the
    # same rendered photo strip and must never trigger additional camera steps.
    print_copies: int = 1


@dataclass(frozen=True)
class OrderQuote:
    """Consistent DEMO checkout math for session fees and printed sheets."""

    session_count: int
    print_copy_count: int
    session_subtotal: int
    print_subtotal: int
    total_amount: int


def quote_order(templates: Sequence[BoothTemplate], quantities: Mapping[str, int]) -> OrderQuote:
    """Price one 3-photo session per selected design and one fee per paper copy.

    Nonzero picker quantities are copy counts. Reuse planning validation so
    displayed cart totals cannot differ from the capture and print plan.
    """
    plans = build_session_plans(templates, quantities)
    sessions = len(plans)
    copies = sum(plan.print_copies for plan in plans)
    session_fee = sessions * PRICE_PER_SESSION
    copy_fee = copies * PRICE_PER_PRINT_COPY
    return OrderQuote(sessions, copies, session_fee, copy_fee, session_fee + copy_fee)


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
        # Return true only after three initial photos exist, which is the minimum required to enter
        # review.
        return len(self.initial_photo_paths) == 3

    @property
    def retake_used(self) -> bool:
        # Return whether this session already has a replacement photo, which enforces its one-retake
        # quota.
        return self.retake_path is not None

    @property
    def can_retake(self) -> bool:
        # Combine the review-ready, selected-photo, and unused-quota rules into the single retake
        # eligibility check used by the UI and controller.
        return (
            self.ready_for_review
            and self.selected_index is not None
            and not self.retake_used
        )

    @property
    def raw_photo_paths(self) -> list[Path]:
        # Return every original and replacement capture for the audit trail and upload queue.
        paths = list(self.initial_photo_paths)
        if self.retake_path is not None:
            paths.append(self.retake_path)
        return paths

    @property
    def final_photo_paths(self) -> list[Path]:
        # Return the three photos that should appear in the final strip, replacing the selected
        # position when a retake exists.
        photos = list(self.initial_photo_paths)
        if self.retake_path is not None and self.retake_target_index is not None:
            photos[self.retake_target_index] = self.retake_path
        return photos

    def add_initial_photo(self, path: Path) -> None:
        # Append one initial capture and reject a fourth initial photo so each session always starts
        # with exactly three.
        if len(self.initial_photo_paths) >= 3:
            raise ValueError("This session already has three initial photos.")
        self.initial_photo_paths.append(Path(path))

    def select_photo(self, index: int) -> None:
        # Store the chosen index after validating that all initial captures exist and the index is
        # within the three-photo range.
        if not self.ready_for_review:
            raise ValueError("Capture all three photos before selecting one.")
        if index < 0 or index >= 3:
            raise IndexError("Photo selection must be between 0 and 2.")
        self.selected_index = index

    def apply_retake(self, path: Path) -> None:
        # Attach the retake to the selected position and reject attempts without a selection or after
        # the quota is used.
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
    """Create one capture session for each chosen template, not for each print.

    Picker quantities now mean *physical copies* of the single final layout.
    Preserve one ordered session and retake allowance per selected template.
    Unselected templates generate neither a capture nor a print job.
    """
    template_copies: dict[str, int] = {}
    for template in templates:
        copies = quantities.get(template.template_id, 0)
        if isinstance(copies, bool) or not isinstance(copies, int) or copies < 0:
            raise ValueError("Print copy quantities must be non-negative integers.")
        template_copies[template.template_id] = copies

    selected = [template for template in templates
                if template_copies[template.template_id] > 0]
    total = len(selected)
    plans: list[SessionPlan] = []
    for order_number, template in enumerate(selected, start=1):
        plans.append(
            SessionPlan(
                session_id=f"session_{order_number:03d}",
                template=template,
                order_number=order_number,
                total_sessions=total,
                # Retain the legacy fields for existing manifest consumers:
                # a chosen template always owns exactly one capture session.
                template_session_number=1,
                template_session_count=1,
                print_copies=template_copies[template.template_id],
            )
        )
    return plans
