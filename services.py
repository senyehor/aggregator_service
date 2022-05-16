import platform
import subprocess
from pathlib import Path

from aggregator.logger import logger


def execute_script_get_return_code(script_name: str) -> int:
    args = compose_args_to_run_script_for_system(script_name)
    with subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as p:
        try:
            code = p.wait(timeout=10 * 60)
            output = p.stdout.read().decode("utf-8")
            error = p.stderr.read().decode("utf-8")
        except subprocess.TimeoutExpired:
            logger.error("aggregator took too long")
            return 408
        except:  # noqa Including KeyboardInterrupt, wait handled that.
            p.kill()
            raise
    if code == 0:
        logger.info(f"got following output executing {script_name}:\n{str(output)}")
    else:
        if error:
            logger.error(f"got following error executing {script_name}:\n{str(error)}")
        else:
            logger.error(f"executing {script_name} just returned {code}")
    return code


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
