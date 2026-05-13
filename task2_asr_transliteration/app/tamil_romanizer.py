# app/tamil_romanizer.py
"""
Custom Tamil -> ASCII Romanization (grapheme-based, library-free).

Produces clean, readable ASCII Latin output for environments where Tamil
Unicode rendering is not guaranteed (plain-text logs, terminals, slide
decks, PDFs, ATS systems). Output of every Tamil character is strictly
ASCII; non-Tamil characters in the input (spaces, punctuation, digits,
Latin letters) are passed through verbatim.

Conventions chosen for this project:
  - Long vowels are doubled:           AA, II, UU, OO -> aa, ii, uu, oo
  - Tamil-specific 'ae' for long e:    Tamil EE       -> "ae"
  - Retroflex consonants are uppercase:
        Tamil NA-retroflex            -> N    (e.g. nuNNaRivu)
        Tamil LA-retroflex (zh, La)   -> L    (e.g. tamiL, menporuL)
        Tamil RA-retroflex (Ra)       -> R    (e.g. poRiyaaLar)
  - Soft 's' for Tamil cha/sa.
  - Lowercase 't' for both dental and retroflex 'ta' (visual simplicity).
  - Pulli (virama)  suppresses the consonant's inherent 'a'.
  - Consonant + vowel-sign pairs are emitted together.

This module is deliberately tiny (no external dependency) so the romanization
behaviour is fully under project control and the output exactly matches
what the documentation, presentation and README examples advertise.
"""

# ---------------------------------------------------------------------------
# Independent vowels (uyir)
# ---------------------------------------------------------------------------
_VOWELS = {
    "அ": "a",  "ஆ": "aa", "இ": "i",  "ஈ": "ii",
    "உ": "u",  "ஊ": "uu", "எ": "e",  "ஏ": "ae",
    "ஐ": "ai", "ஒ": "o",  "ஓ": "oo", "ஔ": "au",
}

# ---------------------------------------------------------------------------
# Dependent vowel signs (combining marks that follow a consonant)
# ---------------------------------------------------------------------------
_VOWEL_SIGNS = {
    "\u0BBE": "aa",  # TAMIL VOWEL SIGN AA
    "\u0BBF": "i",   # TAMIL VOWEL SIGN I
    "\u0BC0": "ii",  # TAMIL VOWEL SIGN II
    "\u0BC1": "u",   # TAMIL VOWEL SIGN U
    "\u0BC2": "uu",  # TAMIL VOWEL SIGN UU
    "\u0BC6": "e",   # TAMIL VOWEL SIGN E
    "\u0BC7": "ae",  # TAMIL VOWEL SIGN EE  (Tamil-specific 'ae' style)
    "\u0BC8": "ai",  # TAMIL VOWEL SIGN AI
    "\u0BCA": "o",   # TAMIL VOWEL SIGN O
    "\u0BCB": "oo",  # TAMIL VOWEL SIGN OO
    "\u0BCC": "au",  # TAMIL VOWEL SIGN AU
}

# ---------------------------------------------------------------------------
# Consonants (mey).  Retroflex / Tamil-specific letters are upper-cased
# to visually distinguish them in the romanized form.
# ---------------------------------------------------------------------------
_CONSONANTS = {
    "க": "k",  "ங": "ng", "ச": "s",  "ஞ": "nj",
    "ட": "t",  "ண": "N",  "த": "t",  "ந": "n",
    "ப": "p",  "ம": "m",  "ய": "y",  "ர": "r",
    "ல": "l",  "வ": "v",  "ழ": "L",  "ள": "L",
    "ற": "R",  "ன": "n",
    "ஜ": "j",  "ஶ": "sh", "ஷ": "Sh", "ஸ": "s",  "ஹ": "h",
}

_PULLI    = "\u0BCD"   # TAMIL SIGN VIRAMA  ()
_AYTHAM   = "ஃ"
_INHERENT = "a"        # inherent vowel attached to a bare consonant


def tamil_to_ascii(text: str) -> str:
    """
    Romanize a Tamil-script string into clean ASCII Latin characters.

    Examples
    --------
    >>> tamil_to_ascii("நான் சாப்பிட்டேன்")
    'naan saappittaen'
    >>> tamil_to_ascii("தமிழ் மொழி")
    'tamiL moLi'
    >>> tamil_to_ascii("நான் ஒரு மென்பொருள் பொறியாளர்")
    'naan oru menporuL poRiyaaLar'
    """
    if not text:
        return ""

    out = []
    i, n = 0, len(text)

    while i < n:
        ch = text[i]

        # --- Consonant: may be followed by a vowel sign or by pulli -----
        if ch in _CONSONANTS:
            out.append(_CONSONANTS[ch])
            if i + 1 < n:
                nxt = text[i + 1]
                if nxt in _VOWEL_SIGNS:
                    out.append(_VOWEL_SIGNS[nxt])
                    i += 2
                    continue
                if nxt == _PULLI:
                    # Pure consonant: no vowel.
                    i += 2
                    continue
            # Default: carry the inherent 'a'
            out.append(_INHERENT)
            i += 1
            continue

        # --- Independent vowel ------------------------------------------
        if ch in _VOWELS:
            out.append(_VOWELS[ch])
            i += 1
            continue

        # --- Aytham (rare): emit 'h' ------------------------------------
        if ch == _AYTHAM:
            out.append("h")
            i += 1
            continue

        # --- Anything else: pass through verbatim -----------------------
        out.append(ch)
        i += 1

    return "".join(out)


if __name__ == "__main__":
    # Tiny self-check when run directly.
    _samples = [
        "நான் சாப்பிட்டேன்",
        "தமிழ் மொழி",
        "செயற்கை நுண்ணறிவு",
        "நான் ஒரு மென்பொருள் பொறியாளர்",
        "வணக்கம் உலகம்",
    ]
    print(f"{'Tamil':40} -> Romanized ASCII")
    print("-" * 80)
    for s in _samples:
        r = tamil_to_ascii(s)
        ok = "ascii" if r.isascii() else "NON-ASCII"
        print(f"{s:40} -> {r}   [{ok}]")
