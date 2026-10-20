"""The shape of a listing draft, as the listing assistant model returns it.

Every field carries value, evidence and confidence. value and evidence are
null when the model could not find the field. Evidence is the exact text
the model read; no evidence means the value is a guess.
"""

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PField


class Field(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    value: str | None                             # normalised, or null
    evidence: str | None                          # exact text read, or null
    confidence: float = PField(ge=0.0, le=1.0)    # the model's own estimate


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Field
    category: Field
    condition: Field
    price: Field


class DraftInput(BaseModel):
    """What the CLI reads: the seller's own words and the model's draft."""

    model_config = ConfigDict(extra="forbid")

    seller_text: str
    draft: Draft
