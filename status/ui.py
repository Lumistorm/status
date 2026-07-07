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
    UNICODE_LEVELS = ' ▏▎▍▌▋▊▉█'
    ASCII_LEVELS = '-123456789#'

    def __init__(self, fraction, length, *, color=None, ascii=None):
        self.fraction = fraction
        self.length = length
        self.color = color
        self.ascii = ascii

    def __str__(self):
        length = self. length
        levels = self.ASCII_LEVELS if self.ascii else self.UNICODE_LEVELS
        num_levels = len(levels) - 1
        filled = int(self.fraction * length * num_levels)
        full, partial = divmod(filled, num_levels)

        bar = levels[-1] * full
        if full < length:
            bar += levels[partial]
        bar += levels[0] * (length - len(bar))

        return f'{self.color}[{bar}]{COLOR_RESET}'


class Progress:
    # def __init__(
    #         self, iterable, *, file=None, min_iters=0, min_interval=0.1,
    #         bar_length=10, bar_color=None, text_color=None, description_color=None,
    #         description=None, separator=' ', description_separator=': '
    # ):
    def __init__(
            self, iterable, *, total=None, start=0, file=sys.stderr, description=None,
            bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
            show_count=True, color=None, bar_color=None, min_iters=1, min_interval=0.1,
            max_interval=10.0, unit='items', ascii=False, separator=' ', disable=False
    ):
        if file is None:
            file = sys.stderr

        self.iterable = iterable
        self.total = total
        self.current_index = start

        self.file = file

        self.description = '' if description is None else description
        self.bar_length = bar_length
        self.show_bar = show_bar
        self.show_percent = show_percent
        self.show_eta = show_eta
        self.show_elapsed = show_elapsed
        self.show_count = show_count

        self.color = '' if color is None else COLORS[color.upper()]
        self.bar_color = '' if bar_color is None else COLORS[bar_color.upper()]

        self.min_iters = min_iters
        self.min_interval = min_interval
        self.max_interval = max_interval

        self.unit = unit
        self.ascii = ascii
        self.separator = separator

        self.disable = disable


        # self.bar_color = COLORS[bar_color.upper()] if bar_color else ''
        # self.text_color = COLORS[text_color.upper()] if text_color else ''
        # self.description_color = COLORS[description_color.upper()] if description_color else ''
        #
        # self.description = description
        #
        # self.separator = f'{self.text_color}{separator}{COLOR_RESET}'
        # self.description_separator = f'{self.description_color}{description_separator}{COLOR_RESET}'

        self.last_update_index = 0
        self.last_update_time = 0
        self.elapsed_time = 0

    def __iter__(self):
        iterable = self.iterable
        total = len(self.iterable)
        min_iters = self.min_iters
        min_interval = self.min_interval
        max_interval = self.max_interval

        start_time = perf_counter()

        for item in iterable:
            yield item
            self.current_index += 1

            current_time = perf_counter()
            delta_time = current_time - self.last_update_time
            force_update = delta_time >= max_interval or self.current_index == total
            self.elapsed_time = current_time - start_time

            # not enough indices passed
            if self.current_index - self.last_update_index < min_iters and not force_update:
                continue

            # not enough time passed
            if delta_time < min_interval and not force_update:
                continue

            self.update(self.current_index / total)

            self.last_update_index = self.current_index
            self.last_update_time = current_time

    def update(self, fraction=1.0):
        file = self.file

        text = self.format_text(fraction)

        file.write(text)
        file.flush()

    def format_text(self, fraction):
        total = len(self.iterable)
        seperator = self.separator

        parts = []

        if self.show_bar:
            bar = Bar(fraction, self.bar_length, color=self.bar_color, ascii=self.ascii)
            parts.append(f'{bar}')
        if self.show_percent:
            parts.append(f'{fraction * 100:.1f}%'.ljust(6))
        if self.show_count:
            parts.append(f'{self.current_index:,}/{total:,} {self.unit}')
        if self.show_elapsed:
            parts.append(self.format_time(self.elapsed_time))

        return f'\r{self.color}{self.description}: {seperator.join(parts)}{COLOR_RESET}'

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
        iterable, *, total=None, start=0, file=sys.stderr, description=None,
        bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
        show_count=True, color=None, bar_color=None, min_iters=1, min_interval=0.1,
        max_interval=10.0, unit='items', ascii=False, separator=' ', disable=False
):
    return Progress(
        iterable=iterable, total=total, start=start, file=file, description=description,
        bar_length=bar_length, show_bar=show_bar, show_percent=show_percent, show_eta=show_eta,
        show_elapsed=show_elapsed, show_count=show_count, color=color, bar_color=bar_color,
        min_iters=min_iters, min_interval=min_interval, max_interval=max_interval, unit=unit,
        ascii=ascii, separator=separator, disable=disable,
    )
