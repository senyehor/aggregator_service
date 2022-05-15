import os

from aggregator.logger import logger
from aggregator.aggregation_info import AggregationInfoJSONProcessor
from aggregator.controllers import AggregationController, BoxListenerController


def main():
    scripts_path = os.getenv("AGGREGATOR_SCRIPTS_PATH")
    controller = AggregationController(
        aggregation_info_file_name="aggregation_info",
        run_aggregation_script_name=f"{scripts_path}/run_aggregator",
        aggregation_info_processor=AggregationInfoJSONProcessor(),
        packet_listener_controller=BoxListenerController(
            f"{scripts_path}/stop_box_listener",
            f"{scripts_path}/resume_box_listener"
        )
    )
    logger.info("starting aggregation")
    code = controller.aggregate()
    if code == 0:
        logger.info("completed aggregation successfully")
        return
    logger.error("aggregation failed")


if __name__ == "__main__":
    main()
