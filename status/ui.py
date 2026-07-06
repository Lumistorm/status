import sys
from time import perf_counter
from traceback import format_tb

COLOR_RESET = '\x1b[0m'
COLORS = {
    'BLACK': '\x1b[30m',
    'RED': '\x1b[31m',
    'GREEN': '\x1b[32m',
    'YELLOW': '\x1b[33m',
    'BLUE': '\x1b[34m',
    'MAGENTA': '\x1b[35m',
    'CYAN': '\x1b[36m',
    'WHITE': '\x1b[37m',
}


class Bar:
    BAR_LEVELS = ' ▏▎▍▌▋▊▉█'

    def __init__(self, fraction, length, *, color=None):
        self.fraction = fraction
        self.length = length
        self.color = color

    def __str__(self):
        fraction = self.fraction
        length = self. length
        bar_levels = self.BAR_LEVELS
        num_levels = len(bar_levels) - 1
        filled = fraction * length * num_levels
        full, partial = divmod(int(filled), num_levels)

        bar = bar_levels[-1] * full

        if full < length:
            bar += bar_levels[partial]
            bar += bar_levels[0] * (length - full - 1)

        return f'{self.color}[{bar}]{COLOR_RESET}'


class Progress:
    def __init__(
            self, iterable, *, file=None, min_iters=0, min_interval=0.1,
            bar_length=10, bar_color=None, text_color=None, description_color=None,
            description=None, separator=' ', description_separator=': '
    ):
        if file is None:
            file = sys.stderr

        if description is None:
            description = ''

        self.iterable = iterable
        self.file = file
        self.bar_length = bar_length
        self.min_iters = min_iters
        self.min_interval = min_interval

        self.bar_color = COLORS[bar_color.upper()] if bar_color else ''
        self.text_color = COLORS[text_color.upper()] if text_color else ''
        self.description_color = COLORS[description_color.upper()] if description_color else ''

        self.description = description

        self.separator = f'{self.text_color}{separator}{COLOR_RESET}'
        self.description_separator = f'{self.description_color}{description_separator}{COLOR_RESET}'

        self.current_index = 0
        self.last_update_index = 0
        self.last_update_time = 0
        self.elapsed_time = 0

    def __iter__(self):
        iterable = self.iterable
        total = len(self.iterable)
        min_iters = self.min_iters
        min_interval = self.min_interval
        start_time = perf_counter()

        for item in iterable:
            yield item
            self.current_index += 1

            # not enough index passed
            if self.current_index - self.last_update_index < min_iters:
                continue

            # not enough time passed
            current_time = perf_counter()
            delta_time = current_time - self.last_update_time
            self.elapsed_time = current_time - start_time

            if delta_time < min_interval:
                continue

            self.update(self.current_index / total)

            self.last_update_index = self.current_index
            self.last_update_time = current_time

        self.elapsed_time = perf_counter() - start_time
        self.update()

    def update(self, fraction=1.0):
        file = self.file

        text = self.format_text(fraction)

        file.write(text)
        file.flush()

    def format_text(self, fraction):
        total = len(self.iterable)
        current_index = self.current_index
        bar_length = self.bar_length
        text_color = self.text_color
        desc_color = self.description_color
        sep = self.separator
        desc_sep = self.description_separator
        seconds = self.elapsed_time

        bar = Bar(fraction, bar_length, color=self.bar_color)

        description = f'{desc_color}{self.description}{COLOR_RESET}'
        percent = f'{(fraction * 100):.1f}%'
        percent_text = f'{text_color}{percent:<7}{COLOR_RESET}'
        progress_text = f'{text_color}{current_index:,}/{total:,}{COLOR_RESET}'
        elapsed_text = self.format_time(seconds)

        return f'\r{description}{desc_sep}{percent_text}{sep}{bar}{sep}{progress_text}{sep}{elapsed_text}'

    def format_time(self, seconds):
        if seconds < 1:
            return f'{seconds * 1000:.0f}ms'
        elif seconds < 60:
            return f'{seconds:.1f}s'

        # more than 60 seconds
        minutes, seconds = divmod(seconds, 60)
        if minutes < 60:
            return f'{int(minutes)}m {int(seconds):02d}s'

        # more than 60 minutes
        hours, minutes = divmod(minutes, 60)
        return f'{int(hours)}h {int(minutes):02d}m'


def progress(
        iterable, *, file=None, min_iters=0, min_interval=0.1,
        bar_length=10, bar_color=None, text_color=None, description_color=None,
        description=None, separator=' ', description_separator=': '
):
    return Progress(
        iterable,
        file=file,
        min_iters=min_iters,
        min_interval=min_interval,
        bar_length=bar_length,
        bar_color=bar_color,
        text_color=text_color,
        description_color=description_color,
        description=description,
        separator=separator,
        description_separator=description_separator
    )
