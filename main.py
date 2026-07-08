from status import progress
from tqdm import tqdm
import time


def main():
    large_number = 500_00_000
    for _ in progress(
        range(large_number),
        color='red',
    ):
        pass
        # time.sleep(0.00001)


if __name__ == '__main__':
    import cProfile
    import pstats

    cProfile.run(
        "main()",
        "profile.stats"
    )

    stats = pstats.Stats("profile.stats")

    stats.sort_stats("cumulative")
    stats.print_stats(20)
