# visualization/card_display.py
#
# Renders playing cards as ASCII art in the terminal.
#
# Each card is 7 columns × 5 rows. Red suits (♥ ♦) are colored red;
# black suits (♣ ♠) use the default terminal color. Hands are rendered
# side-by-side, with one space between cards.
#
# Public API:
#   render_card(card_str)                -> list[str]  (5 rows, 7 cols each)
#   render_hidden_card()                 -> list[str]  (5 rows)
#   render_hand(card_strs, hide_first)   -> list[str]  (5 rows, N cards wide)
#   print_hand(card_strs, hide_first)    -> None

# ANSI escape codes
_RED   = "\033[91m"
_DIM   = "\033[2m"
_RESET = "\033[0m"

_RED_SUITS = ("♥", "♦")


def _color(suit_char: str) -> tuple[str, str]:
    """Return (open, close) ANSI codes for a suit character."""
    if suit_char in _RED_SUITS:
        return _RED, _RESET
    return "", ""


def render_card(card_str: str) -> list[str]:
    """
    Render a card string (e.g. "A♥", "10♦", "K♣") as 5 rows of ASCII art.

    Layout example for "A♥":
        ┌─────┐
        │A    │
        │  ♥  │
        │    A│
        └─────┘

    The rank and suit are ANSI-colored for red suits.
    """
    suit_char = card_str[-1]          # always the last character
    rank_str  = card_str[:-1]         # "A", "2"–"10", "J", "Q", "K"

    open_c, close_c = _color(suit_char)

    # Inner width is 5 chars. Rank is left-aligned on top, right-aligned on bottom.
    top    = f"{open_c}{rank_str.ljust(5)}{close_c}"  # e.g. "A    " or "10   "
    middle = f"  {open_c}{suit_char}{close_c}  "      # e.g. "  ♥  "
    bottom = f"{open_c}{rank_str.rjust(5)}{close_c}"  # e.g. "    A" or "   10"

    return [
        "┌─────┐",
        f"│{top}│",
        f"│{middle}│",
        f"│{bottom}│",
        "└─────┘",
    ]


def render_hidden_card() -> list[str]:
    """Render a face-down card (used for the dealer's hole card)."""
    fill = f"{_DIM}░░░░░{_RESET}"
    return [
        "┌─────┐",
        f"│{fill}│",
        f"│{fill}│",
        f"│{fill}│",
        "└─────┘",
    ]


def render_hand(card_strs: list[str], hide_first: bool = False) -> list[str]:
    """
    Render a list of card strings side-by-side.

    Args:
        card_strs:  Card strings like ["A♥", "10♦"].
        hide_first: If True, replace the first card with a face-down card.
                    Used to show only the dealer's upcard during the player's turn.

    Returns:
        5 strings, each representing one row across all cards.
    """
    if not card_strs:
        return [""] * 5

    rendered = []
    for i, cs in enumerate(card_strs):
        if i == 0 and hide_first:
            rendered.append(render_hidden_card())
        else:
            rendered.append(render_card(cs))

    # Zip rows and join with one space between cards
    return [" ".join(col[row] for col in rendered) for row in range(5)]


def print_hand(card_strs: list[str], hide_first: bool = False) -> None:
    """Print a hand directly to stdout."""
    for row in render_hand(card_strs, hide_first=hide_first):
        print(row)
