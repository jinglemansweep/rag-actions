from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import List


class StateMessage(BaseModel):
    """
    State transfer message for transferring state reliably via JSON between GitHub Action jobs/steps
    """

    docs: List[Document] = Field(description="List of Documents", default_factory=list)
    inputs: dict = Field(description="Action Inputs", default_factory=dict)
    outputs: dict = Field(description="Action Outputs", default_factory=dict)
    metadata: dict = Field(description="Action Metadata", default_factory=dict)


"""
Indexer sets "docs"
"""
