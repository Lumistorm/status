from time import time


class Progress:
    def __init__(self, iterable):
        self.iterable = iterable
        self.current_index = 0
        self.last_update_index = 0
        self.min_iters = 1
        self.min_time = 10
        self.last_update_time = 0

    def __iter__(self):
        iterable = self.iterable
        current_index = self.current_index
        last_update_index = self.last_update_index
        min_iters = self.min_iters
        min_time = self.min_time
        last_update_time = self.last_update_time

        for item in iterable:
            yield item
            current_index += 1

            # not enough index passed
            if current_index - last_update_index < min_iters:
                continue

            # not enough time passed
            delta_time = time() - last_update_time
            if delta_time < min_time:
                continue

            self.update()

    def update(self):
        pass
