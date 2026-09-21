"""
Input validation and sanitization guardrails for StudyCraft AI.
Ensures student inputs are meaningful, non-empty, and within safe token budgets.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Represents the outcome of an input validation check."""
    is_valid: bool
    error_message: Optional[str] = None
    character_count: int = 0
    word_count: int = 0
    estimated_tokens: int = 0


def clean_input(text: Optional[str]) -> str:
    """Sanitize raw text input by stripping surrounding whitespace and normalizing line endings."""
    if not text:
        return ""
    return text.replace("\r\n", "\n").strip()


def get_text_stats(text: str) -> dict:
    """Calculate character count, word count, and estimated LLM tokens."""
    cleaned = clean_input(text)
    char_count = len(cleaned)
    words = cleaned.split() if cleaned else []
    word_count = len(words)
    estimated_tokens = int(word_count * 1.3)
    return {
        "character_count": char_count,
        "word_count": word_count,
        "estimated_tokens": estimated_tokens,
    }


def validate_input(
    text: Optional[str],
    min_chars: int = 15,
    max_chars: int = 12000,
    field_name: str = "Input content"
) -> ValidationResult:
    """Validate user input against emptiness, minimum length, maximum length, and repetitive spam."""
    if text is None or not text.strip():
        return ValidationResult(
            is_valid=False,
            error_message=f"{field_name} cannot be empty. Please enter or paste some content.",
            character_count=0,
            word_count=0,
            estimated_tokens=0,
        )

    cleaned = clean_input(text)
    stats = get_text_stats(cleaned)
    char_len = stats["character_count"]

    if char_len < min_chars:
        return ValidationResult(
            is_valid=False,
            error_message=(
                f"{field_name} is too short ({char_len} chars). "
                f"Please provide at least {min_chars} characters for a useful AI response."
            ),
            **stats
        )

    if char_len > max_chars:
        return ValidationResult(
            is_valid=False,
            error_message=(
                f"{field_name} exceeds the maximum limit ({char_len:,}/{max_chars:,} characters). "
                f"Please shorten your input before submitting."
            ),
            **stats
        )

    unique_chars = set(cleaned.replace(" ", "").replace("\n", ""))
    if len(cleaned) > 25 and len(unique_chars) <= 2:
        return ValidationResult(
            is_valid=False,
            error_message=f"{field_name} appears to contain repetitive or meaningless characters.",
            **stats
        )

    return ValidationResult(is_valid=True, error_message=None, **stats)


def validate_qa_pair(
    question: Optional[str],
    draft_answer: Optional[str]
) -> ValidationResult:
    """Validate both the question and the student's draft answer for the Answer Improver."""
    q_val = validate_input(question, min_chars=10, max_chars=4000, field_name="Assignment / Exam Question")
    if not q_val.is_valid:
        return q_val

    a_val = validate_input(draft_answer, min_chars=15, max_chars=8000, field_name="Draft Student Answer")
    if not a_val.is_valid:
        return a_val

    total_chars = q_val.character_count + a_val.character_count
    total_words = q_val.word_count + a_val.word_count
    return ValidationResult(
        is_valid=True,
        error_message=None,
        character_count=total_chars,
        word_count=total_words,
        estimated_tokens=int(total_words * 1.3),
    )