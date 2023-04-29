import subprocess
import json

def run_command(cmd_args, timeout):
    process = subprocess.run(cmd_args, shell=True, capture_output=True, timeout=timeout)
    return process.stdout.decode(), process.stderr.decode(), process.returncode

def pyright_infer(file_path):
    stdout, stderr, r_code = run_command("pyright %s --outputjson" % file_path, 60)
    output = json.loads(stdout)
    for dict in output["generalDiagnostics"]:
        if dict["severity"] == "information":
            print(dict)