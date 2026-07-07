from status import progress
import time


def main():
    large_number = 50_000_000
    for _ in progress(
        range(large_number),
        bar_length=20,
        min_interval=0.1,
        min_iters=5_000_000,
        description='[One billion loop]',
        color='red',
        bar_color='green',
        separator=' | ',
    ):

        pass


if __name__ == '__main__':
    main()
