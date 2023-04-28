import subprocess

def run_command(cmd_args, timeout):
    process = subprocess.run(cmd_args, shell=True, capture_output=True, timeout=timeout)
    return process.stdout.decode(), process.stderr.decode(), process.returncode

def pyright_infer(file_path):
    stdout, stderr, r_code = run_command("pyright %s" % file_path, 60)
    print(r_code)
    if r_code == 0:
        print(stdout)