import os
import shutil

def main():
    print("Starting load_new_v2.py...")
    db_paths = [
        "db/jp/gdp/q", "db/jp/export/m", "db/jp/inflation/m", "db/jp/ppi/m", "db/jp/mxpi/m",
        "db/cn/gdp/q", "db/cn/export/m", "db/cn/inflation/m","db/cn/ppi/m", "db/cn/mxpi/m",
        "db/kr/gdp/q", "db/kr/export/m", "db/kr/inflation/m","db/kr/ppi/m", "db/kr/mxpi/m",
        "db/tw/gdp/q", "db/tw/export/m", "db/tw/inflation/m""db/tw/ppi/m", "db/tw/mxpi/m",  
    ]
    category_map = {
        "gdp": "GDP",
        "export": "Trade",
        "trade": "Trade",
        "inflation": "Inflation",
        "ppi" : 'PPI',
        "mxpi" : "MXPI"
    }

    for path in db_paths:
        abs_path = os.path.abspath(path)
        print(f"Checking path: {abs_path}")
        if not os.path.exists(path):
            print(f"Path does not exist: {abs_path}")
            continue
        split = path.split("/")
        country = split[1]
        cat = split[2]
        freq = split[3]
        all_files = os.listdir(path)
        print(f"Files in {abs_path}: {all_files}")
        for filename in all_files:
            if filename.endswith("_raw.csv"):
                print(f"Found file to process: {filename}")
                new_name = filename.replace("_raw.csv", ".csv")
                print(f"Target .csv name: {new_name}")
                raw_path = os.path.join(path, filename)
                csv_path = os.path.join(path, new_name)
                if os.path.exists(csv_path):
                    print(f"Removing existing file: {csv_path}")
                    os.remove(csv_path)
                cat_key = cat.lower()
                cat_arg = category_map.get(cat_key, cat)
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
                print(f"Copying {raw_path} to {csv_path}")
                shutil.copy(raw_path, csv_path)

if __name__ == "__main__":
    main()