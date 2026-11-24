"""Pushing new bus positions to every open map, the moment they arrive (FR-22)."""

import uuid
from typing import Any

from fastapi import WebSocket


class LiveUpdates:
    """The browsers that have a live map open, and a way to send them all a message.

    The list lives in this server's memory, so it works with one backend process, which is
    what the MVP runs. Several processes would need a shared message service instead.
    """

    def __init__(self) -> None:
        self._maps: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a map that wants live updates."""
        await websocket.accept()
        self._maps.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Forget a map that has closed."""
        self._maps.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send the message to every open map; drop any that can no longer receive."""
        for websocket in list(self._maps):
            try:
                await websocket.send_json(message)
            except Exception:  # the phone lost signal or closed the tab without saying goodbye
                self.disconnect(websocket)


def journey_ended_message(journey_id: uuid.UUID) -> dict[str, Any]:
    """Tells open maps to remove a bus whose journey is over."""
    return {"type": "journey_ended", "journey_id": str(journey_id)}


live_updates = LiveUpdates()
