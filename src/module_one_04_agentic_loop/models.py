from dataclasses import dataclass
from typing import Union


@dataclass
class BookingRequest:
    goal: str


@dataclass
class BookingResult:
    message: str  # Summary of what was accomplished
    steps_taken: list[str]  # List of steps the AI took


@dataclass
class ToolArgument:
    name: str
    type: str
    description: str


@dataclass
class ToolDefinition:
    name: str
    description: str
    arguments: list[ToolArgument]


@dataclass
class AIDecision:
    tool: str
    parameters: dict[str, Union[str, int]]
