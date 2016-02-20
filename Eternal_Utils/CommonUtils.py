import os


class CommonUtils:
    def __init__(self):
        self.test = ""

    @staticmethod
    def get_environ_variable(var_name):
        try:
            return os.environ[var_name]
        except KeyError:
            env_file_path = os.getcwd() + '/../Eternal_Utils/utils.env'
            env_file = open(env_file_path, 'r')
            for line in env_file:
                key_values = line.split('=')
                if key_values[0] == var_name:
                    return key_values[1].replace('\n', '')

        return None
