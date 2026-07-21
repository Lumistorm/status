import sys
from time import perf_counter


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
CLEAR_LINE = '\x1b[2K\r'
UNICODE_LEVELS = ' ▏▎▍▌▋▊▉█'
ASCII_LEVELS = '-123456789#'


class Progress:
    __slots__ = (
        'iterable', 'total', 'current_index', 'file',
        'description', 'bar_length', 'show_bar', 'show_percent', 'show_eta',
        'show_elapsed', 'show_count', '_text_color', '_bar_color', 'min_iters',
        'dynamic_min_iters', 'min_interval', 'unit', 'use_ascii', 'separator',
        'disable', 'leave', 'start_time', 'last_update_time', 'elapsed_time',
        '_bar_levels', 'text', 'use_chunks', '_bar_levels_max_index', '_bar_cache',
        '_bar_cache_filled',
    )

    def __init__(
            self, iterable, *, total=None, start=0, file=sys.stderr, description=None,
            bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
            show_count=True, text_color=None, bar_color=None, min_iters=None, min_interval=0.1,
            unit='it', use_ascii=False, separator=' ', disable=False,
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

        use_chunks = dynamic_min_iters or min_iters > 256

        self.file = file

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

        self.text_color = text_color
        self.bar_color = bar_color

        self.min_iters = min_iters
        self.dynamic_min_iters = dynamic_min_iters
        self.min_interval = min_interval
        self.use_chunks = use_chunks

        self.unit = unit
        self.use_ascii = use_ascii
        self.separator = separator

        self.disable = disable
        self.leave = leave

        self.start_time = perf_counter()
        self.last_update_time = self.start_time
        self.elapsed_time = 0

        self._bar_levels = ASCII_LEVELS if self.use_ascii else UNICODE_LEVELS
        self._bar_levels_max_index = len(self._bar_levels) - 1
        self._bar_cache = ''
        self._bar_cache_filled = -1

        self.text = ''

        self.update(0)

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = '' if value is None else COLORS.get(value.upper(), '')

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
        use_chunks = self.use_chunks
        last_update_time = self.last_update_time

        accumulated_iters = 0
        iters_since_chunk = 0

        update = self.update
        time = perf_counter

        try:
            if use_chunks:

                # Upper boundary of CPython's small integer cache
                small_int_max = 256
                chunk_size = min(small_int_max, min_iters)

                for item in iterable:
                    yield item

                    # Use chunks to keep integer comparison under 256
                    # to take advantage of CPython cached int -5 - 256

                    iters_since_chunk += 1

                    if iters_since_chunk < chunk_size:
                        continue

                    accumulated_iters += iters_since_chunk
                    iters_since_chunk = 0

                    if accumulated_iters < min_iters:
                        chunk_size = min(small_int_max, min_iters - accumulated_iters)
                        continue

                    n += accumulated_iters
                    accumulated_iters = 0

                    current_time = time()
                    delta_time = current_time - last_update_time

                    # not enough time passed
                    if delta_time < min_interval:
                        if dynamic_min_iters:
                            min_iters = max(min_iters + 1, int(min_iters * (min_interval / delta_time)))
                        chunk_size = min(small_int_max, min_iters)
                        continue

                    update(n - last_update_n, current_time)

                    chunk_size = min(small_int_max, min_iters)
                    last_update_time = current_time
                    last_update_n = n
            else:
                for item in iterable:
                    yield item

                    accumulated_iters += 1

                    if accumulated_iters < min_iters:
                        continue

                    n += accumulated_iters
                    accumulated_iters = 0

                    current_time = time()
                    delta_time = current_time - last_update_time

                    # not enough time passed
                    if delta_time < min_interval:
                        if dynamic_min_iters:
                            min_iters = max(min_iters + 1, int(min_iters * (min_interval / delta_time)))
                        continue

                    update(n - last_update_n, current_time)

                    last_update_time = current_time
                    last_update_n = n
        finally:
            # update remaining
            n += accumulated_iters
            if last_update_n < n:
                update(n - last_update_n)

            self.close()

    def update(self, n=1, current_time=None):
        if self.disable:
            return

        if current_time is None:
            current_time = perf_counter()

        self.current_index += n
        self.last_update_time = current_time
        self.elapsed_time = current_time - self.start_time

        fraction = (self.current_index / self.total) if self.total else 0.0
        self.text = self.format_text(fraction)

        self.refresh()

    def refresh(self):
        text = self.text

        if text:
            file = self.file
            file.write(text)
            file.flush()

    def write(self, message):
        if self.disable:
            return

        file = self.file

        file.write(f'{CLEAR_LINE}{message}\n')
        self.refresh()

    def close(self):
        file = self.file

        if self.leave:
            file.write('\n')
        else:
            file.write(CLEAR_LINE)

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
                parts.append(self.format_bar(fraction))

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

        return f'{CLEAR_LINE}{self._text_color}{self.description}{separator.join(parts)}{COLOR_RESET}'

    def format_bar(self, fraction):
        length = self.bar_length
        levels = self._bar_levels
        num_levels = self._bar_levels_max_index
        filled = int(fraction * length * num_levels)

        if filled != self._bar_cache_filled:
            full, partial = divmod(filled, num_levels)

            bar = levels[-1] * full
            if full < length:
                bar += levels[partial]
            bar += levels[0] * (length - len(bar))

            self._bar_cache_filled = filled
            self._bar_cache = bar

        return f'{self._bar_color}[{self._bar_cache}]{self._text_color}'

    @staticmethod
    def format_time(seconds, *, min_unit='ms', precision=0):
        precision = f'.{precision}f'

        if seconds < 1 and min_unit == 'ms':
            return f'{seconds * 1000:{precision}}ms'
        if seconds < 60:
            return f'{seconds:{precision}}s'

        # more than 60 seconds
        minutes, seconds = divmod(int(seconds), 60)
        if minutes < 60:
            if min_unit == 'min':
                return f'{minutes}m'

            return f'{minutes}m {seconds:02d}s'

        # more than 60 minutes
        hours, minutes = divmod(minutes, 60)
        if min_unit == 'h':
            return f'{hours}h'

        return f'{hours}h {minutes:02d}m'


def progress(
        iterable, *, total=None, start=0, file=sys.stderr, description=None,
        bar_length=10, show_bar=True, show_percent=True, show_eta=True, show_elapsed=True,
        show_count=True, text_color=None, bar_color=None, min_iters=None, min_interval=0.1,
        unit='it', use_ascii=False, separator=' ', disable=False, leave=True,
):
    return Progress(
        iterable=iterable, total=total, start=start, file=file, description=description,
        bar_length=bar_length, show_bar=show_bar, show_percent=show_percent, show_eta=show_eta,
        show_elapsed=show_elapsed, show_count=show_count, text_color=text_color, bar_color=bar_color,
        min_iters=min_iters, min_interval=min_interval, unit=unit, use_ascii=use_ascii,
        separator=separator, disable=disable, leave=leave,
    )
