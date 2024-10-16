# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import Self

from pydantic import BaseModel

from ai_tool_lib.utils.uuid import _generate_uuid


class BotSession(BaseModel):
    uid: str
    """ Unique ID for this session. """

    created: datetime.datetime
    """ Time the session was created. """

    updated: datetime.datetime
    """ Time the session was last updated. """

    name: str | None = None
    """ User friendly name for the session. """

    messages: list[dict]
    """ Bot messages from previous sessions. """

    @classmethod
    def new(cls) -> Self:
        """Create a new session."""
        now = datetime.datetime.now(tz=datetime.UTC)
        return cls(uid=_generate_uuid(), created=now, updated=now, messages=[])
