from status import progress
from tqdm import tqdm
import time


def main():
    large_number = 50_000_000
    for _ in progress(
        range(large_number),
        color='red',
        # min_iters=0.1
    ):

        pass


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
