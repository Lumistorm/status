from status import progress
import time


def main():
    large_number = 50_000_000
    for _ in progress(
        range(large_number),
        bar_length=20,
        min_interval=0.1,
        description='[One billion loop]',
        text_color='red',
        bar_color='green',
        description_color='red',
        separator=' | ',
        description_separator=': '
    ):

        pass


if __name__ == '__main__':
    main()
