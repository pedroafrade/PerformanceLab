"""Lossless, lazy persistence for workout sensor series."""

from base64 import b64decode, b64encode
from dataclasses import dataclass
from gzip import compress, decompress
import json


_ENCODING_KEY = "__performancelab_sensor_encoding__"
_MARKER = "gzip-json-v1"


@dataclass(frozen=True)
class CompressedSensor:
    """One losslessly compressed sensor value loaded only on demand."""

    payload: str

    def read(self):
        raw = decompress(
            b64decode(self.payload.encode("ascii"))
        )
        return json.loads(raw.decode("utf-8"))

    def storage_value(self) -> dict[str, str]:
        return {
            _ENCODING_KEY: _MARKER,
            "payload": self.payload,
        }


def sensor_to_storage(value):
    """Return a JSON-compatible, lossless compressed representation."""

    if isinstance(value, CompressedSensor):
        return value.storage_value()

    raw = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    return CompressedSensor(
        b64encode(
            compress(raw, compresslevel=6)
        ).decode("ascii")
    ).storage_value()


def sensor_from_storage(value):
    """Restore a lazy sensor or accept a legacy uncompressed value."""

    if (
        isinstance(value, dict)
        and value.get(_ENCODING_KEY) == _MARKER
        and isinstance(value.get("payload"), str)
    ):
        return CompressedSensor(value["payload"])

    return value
