from functools import wraps
import json
from aiocache.serializers import BaseSerializer
from geopy import Location as GeoLocation
class LocationSerializer(BaseSerializer):
    def dumps(self, value: GeoLocation):
        return json.dumps({
            "address": value.address,
            "point": tuple(value.point),
            "raw": value.raw,
        }).encode()
    def loads(self, value: bytes) -> GeoLocation | None:
        try:
            data = json.loads(value.decode())
            return GeoLocation(**data)
        except (json.JSONDecodeError, AttributeError):
            return None