from time import strftime, localtime
from src.settings import debug_mode
from inspect import currentframe

class Colors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Logger:
    def __init__(self, log_to_console : bool, log_to_file : bool, log_file_path : str = None) -> None:
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console

        self.log_file_path = log_file_path

    def _get_caller_info(self) -> str:
        return currentframe().f_back.f_back.f_back.f_globals["__name__"]

    def _log(self, level : str, message : str, bypass_anti_debug: bool) -> None:
        if not bypass_anti_debug and not debug_mode:
            return

        caller = self._get_caller_info()
        timestamp = strftime("%H:%M:%S", localtime())
        message = f"[{timestamp}] [{Colors.PURPLE}{caller}{Colors.END}] {level}: {message}"

        if self.log_to_console:
            print(message)

        if self.log_to_file:
            with open(self.log_file_path, "w") as log_file:
                log_file.write(message)

    def info(self, message : str, bypass_anti_debug : bool = False) -> None:
        self._log(level=f"{Colors.BLUE}{Colors.BOLD}{'INFO':<7}{Colors.END}", message=message, bypass_anti_debug=bypass_anti_debug)

    def warning(self, message : str, bypass_anti_debug : bool = False) -> None:
        self._log(level=f"{Colors.YELLOW}{Colors.BOLD}{'WARNING':<7}{Colors.END}", message=message, bypass_anti_debug=bypass_anti_debug)

    def error(self, message : str, bypass_anti_debug : bool = False) -> None:
        self._log(level=f"{Colors.RED}{Colors.BOLD}{'ERROR':<7}{Colors.END}", message=message, bypass_anti_debug=bypass_anti_debug)

    def debug(self, message : str) -> None:
        self._log(level=f"{Colors.CYAN}{Colors.BOLD}{'DEBUG':<7}{Colors.END}", message=message, bypass_anti_debug=False)
        
logger = Logger(log_to_console=True, log_to_file=False)