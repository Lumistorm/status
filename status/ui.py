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
PREFIX = '\x1b[K'
UNICODE_LEVELS = ' ▏▎▍▌▋▊▉█'
ASCII_LEVELS = '-123456789#'


class Progress:
    def __init__(
            self, iterable, *, total=None, start=0, file=sys.stderr, description=None,
            bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
            show_count=True, color=None, bar_color=None, min_iters=1, min_interval=0.1,
            max_interval=10.0, unit='items', ascii=False, separator=' ', disable=False,
            leave=True
    ):
        if file is None:
            file = sys.stderr

        self.iterable = iterable

        if total is None:
            try:
                total = len(iterable)
            except TypeError:
                total = None

        self.total = total

        if total is None:
            self.current_index = max(0, start)

        else:
            self.current_index = min(max(0, start), total)

        self.file = file

        description = '' if description is None else description
        self.description = f'{description}: '

        self.bar_length = bar_length
        self.show_bar = show_bar
        self.show_percent = show_percent
        self.show_eta = show_eta
        self.show_elapsed = show_elapsed
        self.show_count = show_count

        self.color = '' if color is None else COLORS.get(color.upper(), '')
        self.bar_color = '' if bar_color is None else COLORS.get(bar_color.upper(), '')

        self.min_iters = min_iters
        self.min_interval = min_interval
        self.max_interval = max_interval

        self.unit = unit
        self.ascii = ascii
        self.separator = separator

        self.disable = disable
        self.leave = leave

        self.last_update_index = 0
        self.start_time = perf_counter()
        self.last_update_time = self.start_time
        self.elapsed_time = 0

        self.bar_levels = ASCII_LEVELS if self.ascii else UNICODE_LEVELS

        self.update(0)

    def __iter__(self):
        if self.disable:
            yield from self.iterable
            return

        current_index = self.current_index

        for item in self.iterable:
            yield item

            current_index += 1
            delta_time = perf_counter() - self.last_update_time
            force_update = delta_time >= self.max_interval or current_index == self.total

            # not enough indices passed
            indices_passed = current_index - self.last_update_index

            if indices_passed < self.min_iters and not force_update:
                continue

            # not enough time passed
            if delta_time < self.min_interval and not force_update:
                continue

            self.update(indices_passed)

        if self.leave:
            self.file.write('\n')
        else:
            self.file.write(f'\r{PREFIX}')

        self.file.flush()

    def update(self, n=1):
        if self.disable:
            return

        current_time = perf_counter()
        self.current_index += n
        self.last_update_index += n
        self.last_update_time = perf_counter()
        self.elapsed_time = current_time - self.start_time

        file = self.file

        fraction = (self.current_index / self.total) if self.total else 0.0
        text = self.format_text(fraction)

        file.write(text)
        file.flush()

    def format_text(self, fraction):
        total = self.total
        separator = self.separator
        current_index = self.current_index
        unit = self.unit
        elapsed = self.elapsed_time

        parts = []

        if total is not None:
            if self.show_bar:
                bar = self.format_bar(fraction)
                parts.append(f'{bar}')

            if self.show_percent:
                parts.append(f'{fraction * 100:.1f}%'.ljust(6))

        if self.show_count:
            if total is None:
                parts.append(f'{current_index:,} {unit}')
            else:
                parts.append(f'{current_index:,}/{total:,} {unit}')

        if self.show_elapsed:
            parts.append(self.format_time(elapsed))

        if self.show_eta and 0 < fraction < 1:
            remaining_time = (elapsed / fraction) - elapsed
            parts.append(f'ETA: {self.format_time(remaining_time, min_unit='s')}')

        return f'\r{PREFIX}{self.color}{self.description}: {separator.join(parts)}{COLOR_RESET}'

    def format_bar(self, fraction):
        length = self.bar_length
        levels = self.bar_levels
        num_levels = len(levels) - 1
        filled = int(fraction * length * num_levels)
        full, partial = divmod(filled, num_levels)

        bar = levels[-1] * full
        if full < length:
            bar += levels[partial]
        bar += levels[0] * (length - len(bar))

        if self.bar_color:
            return f'{self.bar_color}[{bar}]{COLOR_RESET}'

        return f'[{bar}]'

    def format_time(self, seconds, *, min_unit='ms'):
        if seconds < 1 and min_unit == 'ms':
            return f'{seconds * 1000:.0f}ms'
        if seconds < 60:
            return f'{seconds:.1f}s'

        # more than 60 seconds
        minutes, seconds = divmod(seconds, 60)
        if minutes < 60:
            if min_unit == 'min':
                return f'{int(minutes)}m'

            return f'{int(minutes)}m {int(seconds):02d}s'

        # more than 60 minutes
        hours, minutes = divmod(minutes, 60)
        if min_unit == 'h':
            return f'{int(hours)}h'

        return f'{int(hours)}h {int(minutes):02d}m'


def progress(
        iterable, *, total=None, start=0, file=sys.stderr, description=None,
        bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
        show_count=True, color=None, bar_color=None, min_iters=1, min_interval=0.1,
        max_interval=10.0, unit='items', ascii=False, separator=' ', disable=False,
        leave=True
):
    return Progress(
        iterable=iterable, total=total, start=start, file=file, description=description,
        bar_length=bar_length, show_bar=show_bar, show_percent=show_percent, show_eta=show_eta,
        show_elapsed=show_elapsed, show_count=show_count, color=color, bar_color=bar_color,
        min_iters=min_iters, min_interval=min_interval, max_interval=max_interval, unit=unit,
        ascii=ascii, separator=separator, disable=disable, leave=leave,
    )
