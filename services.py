import platform
import subprocess

from aggregator.logger import logger


def execute_script_get_return_code(path: str):
    args = [path] if platform.system() != "Windows" else ["bash.exe", path]
    with subprocess.Popen(args, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as p:
        try:
            code = p.wait(timeout=30)
            output = p.stdout.read()
            error = p.stderr.read()
        except:  # noqa Including KeyboardInterrupt, wait handled that.
            p.kill()
            raise
    if code == 0:
        logger.info(f"got following output executing {path}:\n{output}")
    else:
        if error:
            logger.error(f"got following error executing {path}:\b{error}")
        else:
            logger.error(f"executing {path} just returned 1")
    return code
