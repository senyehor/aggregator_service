import json
from datetime import datetime
from json import JSONEncoder, JSONDecoder
from typing import Callable, Any


class AggregationInfo:
    def __init__(self, time: datetime = None, failed: bool = None, success: bool = None):
        self.__time = datetime.now() if not time else time
        self.__failed = False if failed is None else failed
        self.__success = True if success is None else success
        self.__check_invariant()

    def __repr__(self):
        return f"time is {self.__time} and status is " + "failed" if self.__failed else "ready to aggregate"

    def __check_invariant(self):
        if self.__failed and self.__success:
            raise ValueError("failed and ready to aggregate cannot be true at the same time")

    @property
    def failed(self) -> bool:
        return self.__failed

    @property
    def success(self) -> bool:
        return self.__success

    @property
    def time(self) -> datetime:
        return self.__time


class AggregationInfoJSONProcessor(JSONEncoder, JSONDecoder):
    def encode(self, o: AggregationInfo) -> str:
        dict_representation = {
            "time": o.time.isoformat(),
            "failed": o.failed,
            "success": o.success
        }
        return json.dumps(dict_representation)

    def decode(self, s: str, _w: Callable[..., Any] = ...) -> AggregationInfo:
        dict_representation = json.loads(s)
        try:
            raw_time = dict_representation["time"]
            failed = dict_representation["failed"]
            success = dict_representation["success"]
            time = datetime.fromisoformat(raw_time)
            return AggregationInfo(time=time, failed=failed, success=success)
        except IndexError as e:
            raise ParsingAggregationInfoError(e)
        except ValueError as e:
            ParsingAggregationInfoError(e)


class ParsingAggregationInfoError(Exception):
    pass
