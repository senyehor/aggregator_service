from aggregator.aggregation_info import AggregationInfoJSONProcessor
from aggregator.controllers import AggregationController, BoxListenerController
from aggregator.logger import logger
from aggregator.services import get_module_dir


def main():
    controller = AggregationController(
        aggregation_info_file_path=str(get_module_dir().joinpath("aggregation_info")),
        run_aggregation_script_name="run_aggregator",
        aggregation_info_processor=AggregationInfoJSONProcessor(),
        packet_listener_controller=BoxListenerController(
            "stop_box_listener",
            "resume_box_listener"
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
