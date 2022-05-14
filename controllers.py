import logging

from aggregator.aggregation_info import AggregationInfoJSONProcessor, AggregationInfo, ParsingAggregationInfoError
from aggregator.services import execute_script_get_return_code


class PacketListenerController:
    def __init__(self, stop_packet_listener_script_name: str, resume_packet_listener_script_name: str):
        self.__stop_packet_listener_script_name = stop_packet_listener_script_name
        self.__resume_packet_listener_script_name = resume_packet_listener_script_name

    @staticmethod
    def __try_execute_throw_error_if_fail(script_path: str):
        code = execute_script_get_return_code(script_path)
        if code != 0:
            raise PacketListenerControlError()

    def __stop_packet_listener(self):
        self.__try_execute_throw_error_if_fail(self.__stop_packet_listener_script_name)

    def __resume_packet_listener(self):
        self.__try_execute_throw_error_if_fail(self.__stop_packet_listener_script_name)

    def __enter__(self):
        self.__stop_packet_listener()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is PacketListenerControlError:
            logging.error(f"{exc_val}, {exc_tb}")
            exit(1)
        try:
            self.__resume_packet_listener()
        except PacketListenerControlError as e:
            logging.error(e)
            exit(1)


class AggregationController:
    def __init__(self,
                 aggregation_info_file_name: str, run_aggregation_script_name: str,
                 packet_listener_controller: PacketListenerController,
                 aggregation_info_processor: AggregationInfoJSONProcessor):

        self.__aggregation_info_json_processor = aggregation_info_processor
        self.__aggregation_info_file_name = aggregation_info_file_name
        self.__run_aggregation_script_name = run_aggregation_script_name
        self.__packet_listener_controller = packet_listener_controller

    def aggregate(self):
        aggregation_info = self.__get_previous_aggregation_info()
        if self.__check_previous_aggregation_was_successful_or_no_aggregations_were_made(aggregation_info):
            with self.__packet_listener_controller:
                code = self.__start_aggregation()
                if code != 0:
                    logging.error("failed to aggregate")
                    exit(1)

        if aggregation_info.failed:
            logging.error(f"something went wrong during previous aggregation that was run at {aggregation_info.__time}")
            exit(1)

    def __get_previous_aggregation_info(self) -> AggregationInfo | None:
        try:
            with open(self.__aggregation_info_file_name, "r") as file:
                raw_data = file.read()
                if raw_data:  # case when there were no previous aggregation attempts
                    try:
                        aggregation_info = self.__aggregation_info_json_processor.decode(raw_data)
                        return aggregation_info
                    except ParsingAggregationInfoError:
                        logging.error("failed to parse previous aggregation attempt data")
                        exit(1)
        except FileNotFoundError:
            return None

    @staticmethod
    def __check_previous_aggregation_was_successful_or_no_aggregations_were_made(
            previous_aggregation_info: AggregationInfo) -> bool:

        return not previous_aggregation_info or previous_aggregation_info.success

    def __start_aggregation(self) -> int:
        return execute_script_get_return_code(f"./{self.__run_aggregation_script_name}")

    def __save_aggregation_failed(self):
        info_aggregation_failed = AggregationInfo(failed=True)
        self.__save_aggregation_info(info_aggregation_failed)

    def __save_aggregation_went_successfully(self):
        info_aggregation_success = AggregationInfo(success=True)
        self.__save_aggregation_info(info_aggregation_success)

    def __save_aggregation_info(self, aggregation_info: AggregationInfo):
        with open(self.__aggregation_info_file_name, "w") as file:
            file.write(self.__aggregation_info_json_processor.encode(aggregation_info))


class PacketListenerControlError(Exception):

    def __init__(self, start_fail: bool = False, end_fail: bool = False, *args: object) -> None:
        if start_fail and end_fail:
            raise ValueError("both start_fail and end_fail cannot be true")
        self.start_fail = start_fail
        self.end_fail = end_fail
        super().__init__(*args)
