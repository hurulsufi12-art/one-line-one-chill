"""One Line, One Chill — entry program.

Writes one line (136 chars, gate 1-200) to
/output/entry.txt. Stdlib only, deterministic, no network, no reads.
"""
import os

TEXT = "The baby monitor finally learned my daughter's voice, and tonight it whispered her goodnight from the kitchen while she slept beside me."
MAX_CHARS = 200


def validate(text):
    """Check text against the scorer's gate (RULES.txt).

    UTF-8, 1-MAX_CHARS chars, not whitespace-only, no leading/trailing
    whitespace, single line. Returns the text unchanged when valid,
    otherwise raises SystemExit with a specific reason.
    """
    if not isinstance(text, str):
        raise SystemExit("entry text is not str")
    if not 1 <= len(text) <= MAX_CHARS:
        raise SystemExit(f"entry text length {len(text)} outside 1-{MAX_CHARS}")
    if not text.strip():
        raise SystemExit("entry text is whitespace-only")
    if text != text.strip():
        raise SystemExit("entry text has leading/trailing whitespace")
    if "\n" in text or "\r" in text:
        raise SystemExit("entry text is not a single line")
    if any(ord(ch) < 0x20 for ch in text):
        raise SystemExit("entry text contains a control character (U+0000-U+001F)")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise SystemExit("entry text is not UTF-8 encodable")
    return text


def write_entry(text):
    """Write text atomically to /output/entry.txt, then verify by read-back.

    Temp name carries the pid so two concurrent grader runs never
    overwrite each other's in-flight file. A crash mid-write must never
    leave a truncated entry.txt for the grader to read.
    """
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != text:
            raise SystemExit("entry.txt read-back mismatch after atomic write")
    return final_path


def main():
    text = validate(TEXT)
    write_entry(text)


if __name__ == "__main__":
    main()
