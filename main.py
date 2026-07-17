from status import progress, Progress
import time


def main():
    large_number = 10_000_000
    x = 0
    progress_bar = progress(range(large_number), min_iters=1000,)
    for i in progress_bar:
        x += i * i


if __name__ == '__main__':
    import dis
    dis.dis(Progress.__iter__)
    # import cProfile
    # from pstats import Stats
    #
    # pr = cProfile.Profile()
    # pr.enable()
    #
    # main()
    #
    # pr.disable()
    # stats = Stats(pr)
    # stats.sort_stats('tottime').print_stats(10)
