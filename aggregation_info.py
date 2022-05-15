import json
from datetime import datetime
from json import JSONEncoder, JSONDecoder
from typing import Callable, Any


class AggregationInfo:
    def __init__(self, time: datetime = None, failed: bool = False, success: bool = False):
        self.__time = datetime.now() if not time else time
        self.__failed = failed
        self.__success = success
        self.__check_invariant()

    def __check_invariant(self):
        if self.failed and self.success:
            raise ValueError("failed and success cannot be true at the same time")
        if not (self.failed or self.success):
            raise ValueError("failed and success cannot be false at the same time or you did not provide one of them")

    def __repr__(self):
        return f"time is {self.__time} and status is " + "failed" if self.__failed else "ready to aggregate"

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
        }
        if o.failed:
            dict_representation["failed"] = True
        if o.success:
            dict_representation["success"] = True
        return json.dumps(dict_representation)

    def decode(self, s: str, _w: Callable[..., Any] = ...) -> AggregationInfo:
        dict_representation: dict = json.loads(s)
        try:
            raw_time = dict_representation.get("time")
            failed = dict_representation.get("failed", False)
            success = dict_representation.get("success", False)
            time = datetime.fromisoformat(raw_time)
            return AggregationInfo(time=time, failed=failed, success=success)
        except IndexError as e:
            raise ParsingAggregationInfoError(e)
        except ValueError as e:
            ParsingAggregationInfoError(e)


class ParsingAggregationInfoError(Exception):
    pass
