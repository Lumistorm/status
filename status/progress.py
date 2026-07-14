import sys
from time import time as perf_counter


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
    __slots__ = (
        'iterable', 'total', 'current_index', 'file', 'write', 'flush',
        'description', 'bar_length', 'show_bar', 'show_percent', 'show_eta',
        'show_elapsed', 'show_count', '_color', '_bar_color',
        'min_iters', 'dynamic_min_iters', 'min_interval', 'unit', 'ascii',
        'separator', 'disable', 'leave', 'start_time', 'last_update_time',
        'elapsed_time', 'bar_levels',
    )

    def __init__(
            self, iterable, *, total=None, start=0, file=sys.stderr, description=None,
            bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
            show_count=True, color=None, bar_color=None, min_iters=None, min_interval=0.1,
            unit='items', ascii=False, separator=' ', disable=False,
            leave=True
    ):
        if file is None:
            file = sys.stderr

        if total is None:
            try:
                total = len(iterable)
            except TypeError:
                total = None

        if total is None:
            current_index = max(0, start)

        else:
            current_index = min(max(0, start), total)

        if description is None:
            description = ''
        else:
            description = f'{description}: '

        if min_iters is None:
            min_iters = 0
            dynamic_min_iters = True
        else:
            dynamic_min_iters = False

        self.file = file
        self.write = file.write
        self.flush = file.flush

        self.iterable = iterable
        self.total = total
        self.current_index = current_index

        self.description = description
        self.bar_length = bar_length

        self.show_bar = show_bar
        self.show_percent = show_percent
        self.show_eta = show_eta
        self.show_elapsed = show_elapsed
        self.show_count = show_count

        self.color = color
        self.bar_color = bar_color

        self.min_iters = min_iters
        self.dynamic_min_iters = dynamic_min_iters
        self.min_interval = min_interval

        self.unit = unit
        self.ascii = ascii
        self.separator = separator

        self.disable = disable
        self.leave = leave

        self.start_time = perf_counter()
        self.last_update_time = self.start_time
        self.elapsed_time = 0

        self.bar_levels = ASCII_LEVELS if self.ascii else UNICODE_LEVELS

        self.update(0)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = '' if value is None else COLORS.get(value.upper(), '')

    @property
    def bar_color(self):
        return self._bar_color

    @bar_color.setter
    def bar_color(self, value):
        self._bar_color = '' if value is None else COLORS.get(value.upper(), '')

    def __iter__(self):
        if self.disable:
            yield from self.iterable
            return

        iterable = self.iterable
        n = self.current_index
        last_update_n = n
        min_iters = self.min_iters
        dynamic_min_iters = self.dynamic_min_iters
        min_interval = self.min_interval
        last_update_time = self.last_update_time
        counter = 0

        for item in iterable:
            yield item
            counter += 1

            if counter < min_iters:
                continue

            n += counter
            counter = 0

            current_time = perf_counter()
            delta_time = current_time - last_update_time

            # not enough time passed
            if delta_time < min_interval:
                if dynamic_min_iters:
                    min_iters = max(min_iters + 1, int(min_iters * (min_interval / delta_time)))
                continue

            self.update(n - last_update_n, current_time)

            last_update_time = current_time
            last_update_n = n

        # update remaining
        n += counter
        if last_update_n < n:
            self.update(n - last_update_n)

        if self.leave:
            self.write('\n')
        else:
            self.write(f'\r{PREFIX}')

        self.flush()

    def update(self, n=1, current_time=None):
        if self.disable:
            return

        if current_time is None:
            current_time = perf_counter()

        self.current_index += n
        self.last_update_time = current_time
        self.elapsed_time = current_time - self.start_time

        fraction = (self.current_index / self.total) if self.total else 0.0
        text = self.format_text(fraction)

        self.write(text)
        self.flush()

    def format_text(self, fraction):
        total = self.total
        separator = self.separator
        current_index = self.current_index
        unit = self.unit
        elapsed = self.elapsed_time

        parts = [self.description]

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
            parts.append(self.format_time(elapsed, precision=1))

        if self.show_eta and 0 < fraction < 1:
            remaining_time = (elapsed / fraction) - elapsed
            parts.append(f'ETA: {self.format_time(remaining_time, min_unit='s')}')

        return f'\r{PREFIX}{self._color}{separator.join(parts)}{COLOR_RESET}'

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

        return f'{self._bar_color}[{bar}]{self._color}'

    @staticmethod
    def format_time(seconds, *, min_unit='ms', precision=0):
        precision = f'.{precision}f'

        if seconds < 1 and min_unit == 'ms':
            return f'{seconds * 1000:{precision}}ms'
        if seconds < 60:
            return f'{seconds:{precision}}s'

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
        show_count=True, color=None, bar_color=None, min_iters=None, min_interval=0.1,
        unit='items', ascii=False, separator=' ', disable=False, leave=True,
):
    return Progress(
        iterable=iterable, total=total, start=start, file=file, description=description,
        bar_length=bar_length, show_bar=show_bar, show_percent=show_percent, show_eta=show_eta,
        show_elapsed=show_elapsed, show_count=show_count, color=color, bar_color=bar_color,
        min_iters=min_iters, min_interval=min_interval, unit=unit, ascii=ascii,
        separator=separator, disable=disable, leave=leave,
    )
