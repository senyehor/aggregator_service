import subprocess


def execute_script_get_return_code(path: str):
    return subprocess.call(path, shell=True)
