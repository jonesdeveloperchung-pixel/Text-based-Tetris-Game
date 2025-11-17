class Color:
    """
    A utility class for applying ANSI color and text attribute codes to strings
    for terminal output.
    """
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Standard 8 Colors (Foreground)
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @staticmethod
    def _apply_color(text: str, color_code: str) -> str:
        """Applies a given ANSI color code to text and ensures it's reset."""
        return f"{color_code}{text}{Color.RESET}"

    @staticmethod
    def black(text: str) -> str:
        return Color._apply_color(text, Color.BLACK)

    @staticmethod
    def red(text: str) -> str:
        return Color._apply_color(text, Color.RED)

    @staticmethod
    def green(text: str) -> str:
        return Color._apply_color(text, Color.GREEN)

    @staticmethod
    def yellow(text: str) -> str:
        return Color._apply_color(text, Color.YELLOW)

    @staticmethod
    def blue(text: str) -> str:
        return Color._apply_color(text, Color.BLUE)

    @staticmethod
    def magenta(text: str) -> str:
        return Color._apply_color(text, Color.MAGENTA)

    @staticmethod
    def cyan(text: str) -> str:
        return Color._apply_color(text, Color.CYAN)

    @staticmethod
    def white(text: str) -> str:
        return Color._apply_color(text, Color.WHITE)

    @staticmethod
    def bold(text: str) -> str:
        return Color._apply_color(text, Color.BOLD)

    @staticmethod
    def underline(text: str) -> str:
        return Color._apply_color(text, Color.UNDERLINE)

    @staticmethod
    def bold_red(text: str) -> str:
        return Color._apply_color(text, f"{Color.BOLD}{Color.RED}")

    @staticmethod
    def bold_green(text: str) -> str:
        return Color._apply_color(text, f"{Color.BOLD}{Color.GREEN}")

    @staticmethod
    def bold_yellow(text: str) -> str:
        return Color._apply_color(text, f"{Color.BOLD}{Color.YELLOW}")
