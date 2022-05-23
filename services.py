import platform
import subprocess
from pathlib import Path

from aggregator.logger import logger


class ScriptExecutionResult:
    def __init__(self, code: int, output: str = "", error_output: str = ""):
        self.__code = code
        self.__output = output.strip()
        self.__error_output = error_output.strip()
        self.__validate()

    def __validate(self):
        if self.__code is None:
            raise ValueError("script should necessarily return some code")

    @property
    def code(self) -> int:
        return self.__code

    @property
    def output(self) -> str:
        return self.__output

    @property
    def error_output(self) -> str:
        return self.__error_output

    @property
    def successful(self) -> bool:
        return self.__code == 0

    def __repr__(self) -> str:
        result_verbose = "succeeded" if self.successful else "failed" + f" with code {self.__code}"
        output = f" with output:\n{self.__output}" if self.__output else ""
        error = f" with error:\n{self.__error_output}" if self.__error_output else ""
        if output:
            result_verbose += output
        if error:
            result_verbose += error
        return result_verbose


def execute_script(script_name: str, timeout_seconds: float, include_output: bool = False) -> ScriptExecutionResult:
    args = compose_args_to_run_script_for_system(script_name)
    output_method = subprocess.PIPE if include_output else None
    try:
        logger.debug(f"launched {script_name}")
        result = subprocess.run(args=args, timeout=timeout_seconds, stderr=output_method, stdout=output_method)
        logger.debug(f"finished {script_name}")
        script_stdout = result.stdout.decode("utf-8") if result.stdout else ""
        script_stderr = result.stderr.decode("utf-8") if result.stderr else ""
    except subprocess.TimeoutExpired:
        return ScriptExecutionResult(code=124, error_output=f"timeout reached for {script_name}")
    return ScriptExecutionResult(code=result.returncode, output=script_stdout, error_output=script_stderr)


def check_is_windows() -> bool:
    return platform.system() == "Windows"


def check_is_linux() -> bool:
    return platform.system() == "Linux"


def compose_args_to_run_script_for_system(script_name: str) -> list[str]:
    if check_is_windows():
        return ["bash.exe", f"./scripts/{script_name}"]
    if check_is_linux():
        script_directory_path = Path(__file__).parent.joinpath("scripts")
        script_path = script_directory_path.joinpath(script_name)
        return [str(script_path)]
    logger.error("unexpected system, exiting")
    exit(1)
