class CLIHandler:
    def __init__(self):
        pass

    def execute_command(self, command):
        import subprocess

        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8'), None
        except subprocess.CalledProcessError as e:
            return None, e.stderr.decode('utf-8')