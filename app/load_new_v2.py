import os

def main():
    # list all paths to check
    db_paths = [
        "db/jp/gdp/q", "db/jp/export/m", "db/jp/inflation/m",
        "db/cn/gdp/q", "db/cn/export/m", "db/cn/inflation/m",
        "db/kr/gdp/q", "db/kr/export/m", "db/kr/inflation/m",
        "db/tw/gdp/q", "db/tw/export/m", "db/tw/inflation/m"
    ]

    # check for each path
    for path in db_paths:
        if not os.path.exists(path):
            continue
        split = path.split("/")
        country = split[1]
        cat = split[2]
        freq = split[3]
        # list all files in path
        all_files = os.listdir(path)
        for filename in all_files:
            # check for files named as new
            if filename.endswith("_new.csv"):
                print(filename)
                new_name = filename[:-8] + ".csv"
                print(new_name)

                # remove old raw file if exists
                old_raw_path = os.path.join(path, new_name)
                if os.path.exists(old_raw_path):
                    os.remove(old_raw_path)

                # rename new file to raw
                new_raw_path_src = os.path.join(path, filename)
                new_raw_path_dest = os.path.join(path, new_name)
                os.rename(new_raw_path_src, new_raw_path_dest)

                # run onboarding with new file
                if cat == "gdp":
                    cat_arg = "GDP"
                elif cat == "export":
                    cat_arg = "Trade"
                elif cat == "inflation":
                    cat_arg = "Inflation"
                else:
                    cat_arg = cat
                command = (
                    f"python onboarding_pipeline.py "
                    f"--category {cat_arg} "
                    f"--country {country.upper()} "
                    f"--freq {freq.upper()} "
                    f"--to_output "
                    f"--to_db"
                )
                print("Running:", command)
                os.system(command)

if __name__ == "__main__":
    main()