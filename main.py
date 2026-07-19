from status import progress, Progress
import time


def main():
    large_number = 10_000_000
    x = 0
    progress_bar = progress(range(large_number), min_iters=1000,)
    for i in progress_bar:
        x += i * i


if __name__ == '__main__':
    main()
