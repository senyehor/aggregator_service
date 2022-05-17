from aggregator.aggregation_info import AggregationInfoJSONProcessor, AggregationInfo, ParsingAggregationInfoError
from aggregator.logger import logger
from aggregator.services import execute_script


class BoxListenerController:
    def __init__(self, stop_box_listener_script_name: str, resume_box_listener_script_name: str) -> None:
        self.__stop_box_listener_script_name = stop_box_listener_script_name
        self.__resume_box_listener_script_name = resume_box_listener_script_name

    def __stop_box_listener(self):
        logger.debug("trying to stop box listener")
        execution_result = execute_script(self.__stop_box_listener_script_name, timeout_seconds=60)
        if not execution_result.successful:
            logger.error(str(execution_result))
            raise BoxListenerControlError(stop_fail=True)

    def __resume_box_listener(self):
        logger.debug("trying to resume box listener")
        execution_result = execute_script(self.__resume_box_listener_script_name, timeout_seconds=60)
        if not execution_result.successful:
            logger.error(str(execution_result))
            raise BoxListenerControlError(stop_fail=True)

    def __enter__(self):
        self.__stop_box_listener()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__resume_box_listener()


class AggregationController:
    def __init__(self,
                 aggregation_info_file_name: str, run_aggregation_script_name: str,
                 packet_listener_controller: BoxListenerController,
                 aggregation_info_processor: AggregationInfoJSONProcessor) -> None:
        self.__aggregation_info_json_processor = aggregation_info_processor
        self.__aggregation_info_file_name = aggregation_info_file_name
        self.__run_aggregation_script_name = run_aggregation_script_name
        self.__packet_listener_controller = packet_listener_controller

    def aggregate(self):
        try:
            self.__run_aggregation_process()
            self.__save_aggregation_went_successfully()
            return 0
        except AggregationError:
            self.__save_aggregation_failed()
            return 1

    def __run_aggregation_process(self):
        previous_aggregation_info = self.__get_previous_aggregation_info()
        if not self.__check_previous_aggregation_was_successful_or_no_aggregations_were_made(previous_aggregation_info):
            logger.error(
                f"something went wrong during previous aggregation that was run at {previous_aggregation_info.time}")
            raise AggregationError("something went wrong during previous aggregation")
        logger.debug("previous aggregation not found or was successful")
        try:
            with self.__packet_listener_controller:
                code = self.__run_aggregator()
                if code != 0:
                    logger.error(f"failed to aggregate with return code {code}")
                    raise AggregationError("aggregator return code was not 0")
                return
        except BoxListenerControlError as e:
            logger.error(msg=f"error happened while controlling box listener {e}")
            raise AggregationError from e

    def __get_previous_aggregation_info(self) -> AggregationInfo | None:
        try:
            with open(self.__aggregation_info_file_name, "r") as file:
                raw_data = file.read()
                if raw_data:
                    try:
                        aggregation_info = self.__aggregation_info_json_processor.decode(raw_data)
                        return aggregation_info
                    except ParsingAggregationInfoError:
                        logger.error("failed to parse previous aggregation attempt data")
                        exit(1)
        except FileNotFoundError:  # case when there were no previous aggregation attempts
            return None

    @staticmethod
    def __check_previous_aggregation_was_successful_or_no_aggregations_were_made(
            previous_aggregation_info: AggregationInfo) -> bool:
        return not previous_aggregation_info or previous_aggregation_info.success

    def __run_aggregator(self) -> int:
        logger.debug("trying to start aggregation")
        return execute_script(f"./{self.__run_aggregation_script_name}")

    def __save_aggregation_failed(self):
        info_aggregation_failed = AggregationInfo(failed=True)
        self.__save_aggregation_info(info_aggregation_failed)
        logger.debug("saved aggregation failed")

    def __save_aggregation_went_successfully(self):
        info_aggregation_success = AggregationInfo(success=True)
        self.__save_aggregation_info(info_aggregation_success)
        logger.debug("saved aggregation succeeded")

    def __save_aggregation_info(self, aggregation_info: AggregationInfo):
        with open(self.__aggregation_info_file_name, "w") as file:
            file.write(self.__aggregation_info_json_processor.encode(aggregation_info))


class BoxListenerControlError(Exception):

    def __init__(self, stop_fail: bool = False, resume_fail: bool = False, *args: object) -> None:
        if stop_fail and resume_fail:
            raise ValueError("both stop_fail and resume_fail cannot be true")
        self.stop_fail = stop_fail
        self.resume_fail = resume_fail
        super().__init__(*args)

    def __repr__(self):
        return "stop failed" if self.stop_fail else "resume failed"


class AggregationError(Exception):
    pass
