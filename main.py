from status import progress
import time


def main():
    large_number = 5_0000_000
    for _ in progress(
        range(large_number),
        bar_length=20,
        min_interval=0.1,
        description='[One billion loop]',
        color='red',
        bar_color='green',
        separator=' | ',
        ascii=True
    ):

        pass


if __name__ == '__main__':
    main()
