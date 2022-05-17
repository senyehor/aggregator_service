import platform
import subprocess
from pathlib import Path

from aggregator.logger import logger


class ScriptExecutionResult:
    def __init__(self, code: int, success_output: str = "", error_output: str = ""):
        self.__code = code
        self.__success_output = success_output
        self.__error_output = error_output
        self.__validate()

    def __validate(self):
        if self.__code is None:
            raise ValueError("script should necessarily return some code")
        if self.__success_output and self.__error_output:
            raise ValueError("script cannot return success and error output at the same time")
        if self.__code == 0 and self.__error_output:
            raise ValueError("success code is 0 but error output is present")

    @property
    def code(self) -> int:
        return self.__code

    @property
    def success_output(self) -> str:
        return self.__success_output

    @property
    def error_output(self) -> str:
        return self.__error_output

    @property
    def successful(self) -> bool:
        return self.__code == 0

    @property
    def __repr__(self) -> str:
        if self.__code == 0:
            return f"{self.__success_output} with code {self.__code}"
        return f"{self.__error_output} with code {self.__code}"


def execute_script(script_name: str, timeout_seconds: float) -> ScriptExecutionResult:
    args = compose_args_to_run_script_for_system(script_name)
    with subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as p:
        try:
            code = p.wait(timeout=timeout_seconds)
            output = p.stdout.read().decode("utf-8")
            error = p.stderr.read().decode("utf-8")
        except subprocess.TimeoutExpired:
            return ScriptExecutionResult(code=code, error_output=f"timeout reached for {script_name}")
        except:  # noqa Including KeyboardInterrupt, wait handled that.
            p.kill()
            raise
    return ScriptExecutionResult(code, success_output=output) if output \
        else ScriptExecutionResult(code, error_output=error)


def check_is_windows() -> bool:
    return platform.system() == "Windows"


def check_is_linux() -> bool:
    return platform.system() == "Linux"


def compose_args_to_run_script_for_system(script_name: str) -> list[str]:
    if check_is_windows():
        # I could not figure out how to make bash work with windows paths
        return ["bash.exe", f"./scripts/{script_name}"]
    if check_is_linux():
        script_directory_path = Path(__file__).parent.joinpath("scripts")
        script_path = script_directory_path.joinpath(script_name)
        return [str(script_path)]
    logger.error("unexpected system, exiting")
    exit(1)
