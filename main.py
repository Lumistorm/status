from status import progress


def main():
    large_number = 20_000_000
    a = 0
    progress_bar = progress(range(large_number),)
    for _ in progress_bar:
        if a % 2 == 0:
            a = a * a


if __name__ == '__main__':
    main()
