from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

class Message(BaseModel):
    role: Annotated[str, Field(description="Role of the message sender --> proly the user")]
    content: Annotated[str, Field(description="Content of the message by the user-'role' ")]

class ChatRequest(BaseModel):
    messages: Annotated[list[Message], Field(description="List of messages in the conversation")]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: Optional[List[Recommendation]] = None
    end_of_conversation: bool = False

class HealthResponse(BaseModel):
    status: Annotated[str, Field(description="Current status of the service",default="ok")]
