"""
receipt_parser.py

Purpose:
    Extract structured information from OCR'd doctor's-receipt text.

Notes on robustness:
    OCR output from these receipts is noisy — missing spaces
    ("June14.2024"), garbled words ("Patie nt", "Palfent", "PT"),
    and inconsistent formatting. Every extractor below is written
    to tolerate that noise rather than assume clean text.
"""

import re
import difflib


class ReceiptParser:

    MONTHS = (
        r"(January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
    )

    # Words/labels that should never be mistaken for a hospital name
    NON_HOSPITAL_HINTS = ("total", "amount", "particulars", "description", "patient")

    # Known hospital names for fuzzy-correcting garbled OCR output to
    # a clean canonical form (e.g. "Univerityof Santo Tomasospitai" ->
    # "University of Santo Tomas Hospital"). This is a curated list
    # covering only the hospitals seen so far - it can correct known
    # names, not recognize new ones. Extend this list as you encounter
    # more hospitals, or swap in a real hospital directory lookup for
    # production use.
    KNOWN_HOSPITALS = [
        "Quirino Memorial Medical Center",
        "University of Santo Tomas Hospital",
        "Philippine General Hospital",
        "Cardinal Santos Medical Center",
    ]

    def __init__(self):
        pass

    def parse(self, text, page_number):

        record = {
            "Page": page_number,
            "Receipt No.": self.extract_receipt(text),
            "Doctor Name": self.extract_doctor(text),
            "PRC License": self.extract_prc(text),
            "Hospital": self.extract_hospital(text),
            "Date": self.extract_date(text),
            "Patient Name": self.extract_patient(text),
            "Total Amount (PHP)": self.extract_total(text),
            "Signature": self.extract_signature(text)
        }

        return record

    # ---------------------------------------------------------
    # Receipt Number
    # ---------------------------------------------------------

    def extract_receipt(self, text):
        r"""
        Finds an OR number in whatever shape the OCR produced
        (ORNoOR65116, NoOR-32408, ORW:OR-70675, NaOR-73197, etc.)
        and normalizes the result to "OR-XXXXX".

        Note: assumes the number itself is purely digits, which holds
        for every receipt seen so far. If a future receipt uses an
        alphanumeric OR number, this won't capture the letters - widen
        (\d+) back to [A-Z0-9]+ if that turns out to matter.
        """

        patterns = [
            r"OR\s*No\.?\s*[:\-]?\s*OR[- ]?(\d+)",
            r"ORNo\s*OR[- ]?(\d+)",
            r"ORNo[: ]?(\d+)",
            r"No[: ]?OR[- ]?(\d+)",
            r"ORW[: ]?OR[- ]?(\d+)",
            r"OR[- ]?(\d{4,})"
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.I)

            if match:
                return f"OR-{match.group(1)}"

        return ""

    # ---------------------------------------------------------
    # Doctor Name
    # ---------------------------------------------------------

    def extract_doctor(self, text):

        patterns = [
            r"(Dr\.?\s*[A-Z][A-Za-z .]+)",
            r"(Dr[A-Z][A-Za-z .]+)"
        ]

        for pattern in patterns:

            match = re.search(pattern, text)

            if match:
                return " ".join(match.group(1).split())

        return ""

    # ---------------------------------------------------------
    # PRC License
    # ---------------------------------------------------------

    def extract_prc(self, text):

        patterns = [
            r"(PRC\s*Lic\.?\s*No\.?\s*[A-Za-z0-9]+)",
            r"(PRC\s*LIC\s*No\.?\s*[A-Za-z0-9]+)",
            r"(PRC\s*Lic\s*Na\s*[A-Za-z0-9]+)",
            r"(PRC\s*Lic.*?[0-9]{4,})"
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.I)

            if match:
                return " ".join(match.group(1).split())

        return ""

    # ---------------------------------------------------------
    # Hospital
    # ---------------------------------------------------------

    def extract_hospital(self, text):
        """
        Looks for a line naming a hospital/clinic. Falls back to the
        first "name-like" line (mostly letters) instead of blindly
        taking line 0, since line 0 is often a phone number or OR code.
        """

        keywords = [
            "Hospital",
            "Medical Center",
            "MedicalCentre",
            "MedicalCenter",
            "Clinic",
            "Health Center"
        ]

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        for line in lines:
            for word in keywords:
                if word.lower() in line.lower():
                    return self._normalize_hospital(line)

        # Fallback: first line that looks like a hospital/clinic name
        # rather than a phone number, OR code, or the doctor's/
        # patient's own name line (OCR sometimes misreads "Dr." as
        # "Or."). Restricted to the first 3 lines - the letterhead
        # zone - since scanning further down risks confidently
        # grabbing an unrelated line (e.g. a specialty label) when
        # the real hospital name was simply lost to OCR. A blank
        # result is preferable to a confidently wrong one.
        doctor_name = self.extract_doctor(text)
        doctor_letters = re.sub(r"[^a-z]", "", doctor_name.lower()) if doctor_name else ""

        for line in lines[:3]:

            low = line.lower()

            if any(hint in low for hint in self.NON_HOSPITAL_HINTS):
                continue

            if re.match(r"^(Dr|Or)\.?\s*[A-Z]", line):
                continue

            first_word = low.split()[0] if low.split() else ""
            first_cleaned = re.sub(r"[^a-z]", "", first_word)

            if first_cleaned == "pt" or (
                len(first_cleaned) >= 6 and self._looks_like_patient_label(first_cleaned)
            ):
                continue

            line_letters = re.sub(r"[^a-z]", "", low)

            if doctor_letters and line_letters == doctor_letters:
                continue

            letters = sum(c.isalpha() for c in line)
            digits = sum(c.isdigit() for c in line)

            if letters >= 4 and letters > digits:
                return self._normalize_hospital(line)

        # Nothing plausible found - better to leave it blank than
        # guess wrong (e.g. mislabeling the doctor as the hospital).
        return ""

    def _normalize_hospital(self, raw_line):
        """
        Fuzzy-corrects a raw OCR hospital line against KNOWN_HOSPITALS.
        Falls back to returning the raw line unchanged if nothing in
        the list is a confident enough match, so an unseen hospital
        still gets surfaced (uncorrected) rather than dropped.
        """

        raw_letters = re.sub(r"[^a-z]", "", raw_line.lower())

        best_match = None
        best_ratio = 0.0

        for known in self.KNOWN_HOSPITALS:

            known_letters = re.sub(r"[^a-z]", "", known.lower())
            ratio = difflib.SequenceMatcher(None, raw_letters, known_letters).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = known

        if best_match and best_ratio >= 0.7:
            return best_match

        return raw_line

    # ---------------------------------------------------------
    # Date
    # ---------------------------------------------------------

    def extract_date(self, text):
        """
        Matches "Month Day, Year" even when OCR drops the space
        between month/day ("June14.2024", "August25.2024") or uses a
        period instead of a comma before the year ("August 25.2024").
        """

        pattern = self.MONTHS + r"\s*(\d{1,2})[\., ]*(\d{4})"

        match = re.search(pattern, text, re.I)

        if match:
            month, day, year = match.group(1), int(match.group(2)), match.group(3)
            return f"{month} {day:02d}, {year}"

        return ""

    # ---------------------------------------------------------
    # Patient Name
    # ---------------------------------------------------------

    def extract_patient(self, text):
        """
        Extract patient name from noisy OCR. Handles known garbling
        variants directly ("Patie nt", "Palfent", "PT") rather than
        fuzzy-matching every line, which is simpler and was verified
        against every real sample seen so far.

        The leading \b is required: without it, "PT" (with no word
        boundary) can match inside unrelated text like the tail end
        of "OFFICIALRECEIPT" (...recei-PT), hijacking the match before
        the regex ever reaches the real "Patient <name>" line.
        """

        patterns = [
            r"\b(?:Patient|Patie\s*nt|Palfent|PT)\s+([A-Za-z .]+)",
            r"\b(?:Patient|PT)\s*:?\s*([A-Za-z .]+)"
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.I)

            if match:
                return self._clean_name(match.group(1))

        return ""

    def _looks_like_patient_label(self, word, min_ratio=0.6):

        cleaned = re.sub(r"[^A-Za-z]", "", word).lower()

        if not cleaned:
            return False

        if cleaned in ("pt", "patient"):
            return True

        # Fuzzy match to catch OCR noise like "Palfent"
        ratio = difflib.SequenceMatcher(None, cleaned, "patient").ratio()

        return ratio >= min_ratio

    def _clean_name(self, name):

        name = re.split(r"Date|DESCRIPTION|PARTICULARS|TOTAL|PHP", name, flags=re.I)[0]
        name = re.sub(r"[^A-Za-z .]", "", name).strip()

        return " ".join(name.split())

    # ---------------------------------------------------------
    # Total Amount
    # ---------------------------------------------------------

    def extract_total(self, text):

        amount_re = r"(PHP\s*[\d,]+\.\d{2})"

        lines = text.splitlines()

        # Priority 1: a PHP amount on the same line as "TOTAL",
        # or within the next couple of lines (OCR sometimes pushes
        # the amount a line or two down).
        for i, line in enumerate(lines):

            if "TOTAL" not in line.upper():
                continue

            amount = re.search(amount_re, line, re.I)

            if amount:
                return amount.group(1)

            for offset in (1, 2):

                if i + offset < len(lines):

                    amount = re.search(amount_re, lines[i + offset], re.I)

                    if amount:
                        return amount.group(1)

        # Priority 2: largest PHP amount anywhere in the text
        # (the total is virtually always the largest single line item).
        matches = re.findall(r"PHP\s*([\d,]+\.\d{2})", text, re.I)

        if matches:

            values = [(float(m.replace(",", "")), m) for m in matches]
            largest = max(values)

            return "PHP " + largest[1]

        return ""

    # ---------------------------------------------------------
    # Signature
    # ---------------------------------------------------------

    def extract_signature(self, text):
        """
        NOTE: this is a text-based heuristic and has an inherent
        limitation — it can only tell you whether the receipt
        *mentions* a signature/attestation, not whether a signature
        graphic is actually present on the page. Detecting an actual
        signature mark would require image analysis on the source PDF,
        not OCR text.

        Matching happens in two passes:
          1. Normalized full-phrase match: OCR-inserted spaces (e.g.
             "Atte nding Physician") are stripped out before comparing,
             so they still match the intact phrase.
          2. Fuzzy single-word fallback, restricted to the last few
             lines of the receipt (the footer, where attestation text
             lives). This catches words OCR mangled beyond recognition
             (e.g. "Phmysician"), without matching generic mentions of
             "Physician"/"Doctor" that appear on every receipt's
             letterhead regardless of whether it's actually signed.
        """

        phrases = [
            "Authorized Signature",
            "Authorized Physician",
            "Attending Physician",
            "Signed by",
        ]

        normalized_phrases = [re.sub(r"[^a-z]", "", p.lower()) for p in phrases]

        lines = [l for l in text.splitlines() if l.strip()]

        # Pass 1: per-line, whitespace-normalized phrase match.
        for line in lines:

            line_letters = re.sub(r"[^a-z]", "", line.lower())

            for phrase in normalized_phrases:
                if phrase in line_letters:
                    return "Yes"

        # Pass 2: fuzzy fallback, footer lines only.
        footer_words = ("physician", "signature", "signed", "attending", "authorized")

        for line in lines[-5:]:

            line_letters = re.sub(r"[^a-z]", "", line.lower())

            if not line_letters:
                continue

            for word in footer_words:

                ratio = difflib.SequenceMatcher(None, line_letters, word).ratio()

                if ratio >= 0.75:
                    return "Yes"

        return "No"