import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category")  # in under case
    parser.add_argument("--country")  # in upper case
    parser.add_argument("--freq")  # in upper case
    parser.add_argument("--to_db", action="store_true")  # if true, renew results to DB
    parser.add_argument("--to_output", action="store_true")  # if true, the matching results will be written to db

    args = parser.parse_args()

    # clean raw data
    if args.to_db:
        command = (
            f"python3 clean_raw_data.py "
            f"--category {args.category} "
            f"--country {args.country} "
            f"--freq {args.freq} "
            f"--to_db"
        )
    else:
        command = (
            f"python3 clean_raw_data.py "
            f"--category {args.category} "
            f"--country {args.country} "
            f"--freq {args.freq}"
        )
    os.system(command=command)

    # create data settings
    if args.to_db:
        command = (
            f"python3 create_data_setting.py "
            f"--category {args.category} "
            f"--country {args.country} "
            f"--freq {args.freq} "
            f"--to_db"
        )
    else:
        command = (
            f"python3 create_data_setting.py "
            f"--category {args.category} "
            f"--country {args.country} "
            f"--freq {args.freq}"
        )
    os.system(command=command)

    # match mapping
    if args.to_db:
        if args.to_output:
            command = (
                f"python3 match_mapping.py "
                f"--category {args.category} "
                f"--country {args.country} "
                f"--freq {args.freq}"
                f"--to_output"
                f"--to_db"
            )
        else:
            command = (
                f"python3 match_mapping.py "
                f"--category {args.category} "
                f"--country {args.country} "
                f"--freq {args.freq}"
                f"--to_db"
            )
    else:
        if args.to_output:
            command = (
                f"python3 match_mapping.py "
                f"--category {args.category} "
                f"--country {args.country} "
                f"--freq {args.freq}"
                f"--to_output"
            )
        else:
            command = (
                f"python3 match_mapping.py "
                f"--category {args.category} "
                f"--country {args.country} "
                f"--freq {args.freq}"
            )

    os.system(command=command)


if __name__ == "__main__":
    main()
