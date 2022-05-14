#!usr/bin/python3.10
import json
import logging
import subprocess

from datetime import datetime

from json import JSONEncoder, JSONDecoder
from os import PathLike
from typing import Any, Callable

from aggregator.aggregation_info import AggregationInfoJSONProcessor
from aggregator.controllers import AggregationController, PacketListenerController

logging.basicConfig(filename="aggregation_script.log")


def main():
    controller = AggregationController(
        aggregation_info_file_name="aggregation_info",
        run_aggregation_script_name="run_aggregator",
        aggregation_info_processor=AggregationInfoJSONProcessor(),
        packet_listener_controller=PacketListenerController(
            "stop_packet_listener",
            "resume_packet_listener"
        )
    )
    controller.aggregate()


if __name__ == "__main__":
    main()
