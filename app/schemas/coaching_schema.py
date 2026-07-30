"""
coaching_schema.py

Schemas for AI coaching API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel


class CoachingResponse(BaseModel):
    """
    AI coaching response schema.
    """

    summary: str

    strengths: list[str]

    weaknesses: list[str]

    recommendations: list[str]
