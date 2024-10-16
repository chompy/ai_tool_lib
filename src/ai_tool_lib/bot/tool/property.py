# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Self, TypeVar

from ai_tool_lib.error.tool import (
    ToolPropertyChoiceTypeError,
    ToolPropertyInvalidError,
    ToolPropertyMissingError,
    ToolPropertyTypeError,
)

T = TypeVar("T", bound=type)

PROPERTY_TYPE_NAMES = {str: "string", int: "integer", float: "number", dict: "object", list: "array", bool: "boolean"}


class PropertyDefinition:
    """A property value and its constraints."""

    def __init__(
        self,
        name: str,
        property_type: T,
        description: str = "",
        range_min: int | None = 0,
        range_max: int | None = 0,
        choices: list[T] | None = None,
        *,
        required: bool = False,
    ):
        self.name = name
        if property_type not in PROPERTY_TYPE_NAMES:
            err_msg = f"type {property_type!s} is not a valid property type for property definition"
            raise ToolPropertyTypeError(err_msg)
        self.property_type = property_type
        self.description = description
        self.range_min = range_min
        self.range_max = range_max
        self.choices = choices
        self.required = required

    @classmethod
    def from_dict(cls, data: dict[str, dict]) -> list[Self]:
        out = []
        for k, v in data.items():
            if "type" in v and isinstance(v["type"], str):
                for property_type, name in PROPERTY_TYPE_NAMES.items():
                    if name == v["type"]:
                        v["property_type"] = property_type
                        break
            out.append(cls(name=k, **v))
        return out

    def to_dict(self) -> dict:
        out: dict[str, object] = {
            "type": PROPERTY_TYPE_NAMES[self.property_type],
            "description": self.description,
        }
        if issubclass(self.property_type, (int, float)):
            if self.range_min:
                out["minimum"] = self.range_min
            if self.range_max:
                out["maximum"] = self.range_max
        elif issubclass(self.property_type, list):
            # TODO: allow list of other types
            out["items"] = {"type": "string"}

        # type check choices
        if self.choices:
            for i, choice in enumerate(self.choices):
                if not isinstance(choice, self.property_type):
                    err_msg = f"property definition choice at index {i} is invalid type"
                    raise ToolPropertyChoiceTypeError(err_msg)
            out["enum"] = self.choices

        return out

    def check_value(self, value: Any | None, tool_name: str = "(unknown tool)"):
        if self.required and value is None:
            raise ToolPropertyMissingError(tool_name=tool_name, property_name=self.name)
        if value is not None:
            if not isinstance(value, self.property_type):
                raise ToolPropertyInvalidError(
                    tool_name=tool_name,
                    property_name=self.name,
                    why=f"Value the wrong type, expected {PROPERTY_TYPE_NAMES[self.property_type]}.",
                )
            if isinstance(value, (int, float)) and (
                self.range_max and value > self.range_max or self.range_min and value < self.range_min
            ):
                raise ToolPropertyInvalidError(
                    tool_name=tool_name, property_name=self.name, why="Value is out of range."
                )
            if self.choices and value not in self.choices:
                valid_choices = ",".join([str(c) for c in self.choices])
                raise ToolPropertyInvalidError(
                    tool_name=tool_name,
                    property_name=self.name,
                    why=f"Value is not a valid choice. [Valid choices are: {valid_choices}]",
                )
