from status import progress


def main():
    large_number = 500_00_000
    a = 0
    for _ in progress(
        range(large_number),
        color='red',
        min_iters=50_000_000
    ):
        a -= 1
    print(a)


if __name__ == '__main__':
    main()
