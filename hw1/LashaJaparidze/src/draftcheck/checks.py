"""decide(): route a listing draft before the seller sees the form.

Pure: no network, no model call, no clock, no files. The model drafts;
this code decides which fields may be prefilled.

Flags, checked per field in this order (first match wins), then format:
  missing            value null or blank                        hard
  no_evidence        evidence null or blank                     hard
  price_not_in_text  price evidence not in the seller's text    hard  (never price from a photo)
  not_in_text        other evidence not in the seller's text    soft  (e.g. read from the photo)
  low_confidence     confidence below LOW_CONFIDENCE            soft
  invalid_condition  not one of CONDITIONS                      hard
  invalid_price      not a non-negative amount, <= 2 decimals   hard
  price_mismatch     no number in the evidence equals the price hard

Routes:
  rejected   all four values null: nothing item-like
  review     any hard flag; hard fields are blank in the form, never prefilled
  confirm    soft flags only; everything prefilled, flagged fields highlighted
  accepted   no flags; the seller still presses Publish
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .draft import Draft

REQUIRED = ("title", "category", "condition", "price")
CONDITIONS = ("new", "like_new", "good", "fair", "poor")   # same as the listing model
LOW_CONFIDENCE = 0.6
HARD = {"missing", "no_evidence", "price_not_in_text",
        "invalid_condition", "invalid_price", "price_mismatch"}

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")

REASON_TEXT = {
    "missing": "{F}: not found in your description. Please fill it in.",
    "no_evidence": "{F}: the assistant suggested a value but could not show where you said it. Please fill it in.",
    "price_not_in_text": "Price: you did not write a price. Please type the price you want.",
    "not_in_text": "{F}: suggested from your photo, not your text. Is it right?",
    "low_confidence": "{F}: the assistant is not sure. Please check it.",
    "invalid_condition": "Condition: please pick one of new, like new, good, fair or poor.",
    "invalid_price": "Price: this is not a valid amount. Please type it, for example 25.00.",
    "price_mismatch": "Price: the suggested amount does not match the number you wrote. Please type it.",
}

ROUTE_TEXT = {
    "accepted": "Draft ready. Check it, then press Publish.",
    "confirm": "Please check the highlighted fields, then press Publish.",
    "review": "Some fields are empty. Please fill them in before you publish.",
    "rejected": "We could not find an item for sale here. Describe the item, its condition and your price.",
}


@dataclass
class Decision:
    route: str
    flags: list[tuple[str, str]]       # (flag, field)
    hard: set[str]                     # fields the seller must type; never prefilled
    form: dict[str, str | None]        # what the seller's form shows

    def reasons(self) -> list[str]:
        return [REASON_TEXT[k].format(F=n.capitalize()) for k, n in self.flags]

    def to_json(self) -> dict:
        return {
            "route": self.route,
            "message": ROUTE_TEXT[self.route],
            "flags": [{"flag": k, "field": n, "reason": r}
                      for (k, n), r in zip(self.flags, self.reasons())],
            "hard": sorted(self.hard),
            "form": self.form,
        }


def _norm(text: str) -> str:
    return " ".join(text.casefold().split())


def found_in(evidence: str, source: str) -> bool:
    """Evidence appears in the source text, ignoring case and repeated whitespace."""
    return _norm(evidence) in _norm(source)


def parse_price(value: str) -> Decimal | None:
    """A non-negative amount with at most two decimals, as Decimal('25.00'); else None."""
    try:
        amount = Decimal(value.strip())
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
        return None
    return amount.quantize(Decimal("0.01"))


def numbers_in(text: str) -> set[Decimal]:
    return {Decimal(n.replace(",", ".")) for n in NUMBER.findall(text)}


def _blank(s: str | None) -> bool:
    return s is None or not s.strip()


def decide(draft: Draft, seller_text: str) -> Decision:
    flags: list[tuple[str, str]] = []
    for name in REQUIRED:
        f = getattr(draft, name)
        if _blank(f.value):                              flags.append(("missing", name))
        elif _blank(f.evidence):                         flags.append(("no_evidence", name))
        elif not found_in(f.evidence, seller_text):
            flags.append(("price_not_in_text" if name == "price" else "not_in_text", name))
        elif f.confidence < LOW_CONFIDENCE:              flags.append(("low_confidence", name))

    condition = draft.condition.value
    if not _blank(condition) and condition not in CONDITIONS:
        flags.append(("invalid_condition", "condition"))

    price = draft.price
    amount = None if _blank(price.value) else parse_price(price.value)
    if not _blank(price.value) and amount is None:
        flags.append(("invalid_price", "price"))
    elif amount is not None and not _blank(price.evidence) and amount not in numbers_in(price.evidence):
        flags.append(("price_mismatch", "price"))

    if all(_blank(getattr(draft, n).value) for n in REQUIRED):
        return Decision("rejected", flags, set(), {n: None for n in REQUIRED})

    hard = {n for k, n in flags if k in HARD}
    form = {n: None if n in hard else getattr(draft, n).value.strip() for n in REQUIRED}
    if form["price"] is not None:
        form["price"] = str(amount)
    route = "review" if hard else "confirm" if flags else "accepted"
    return Decision(route, flags, hard, form)
