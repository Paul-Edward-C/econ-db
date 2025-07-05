import os
import shutil

def main():
    db_paths = [
        "db/jp/gdp/q", "db/jp/export/m", "db/jp/inflation/m",
        "db/cn/gdp/q", "db/cn/export/m", "db/cn/inflation/m",
        "db/kr/gdp/q", "db/kr/export/m", "db/kr/inflation/m",
        "db/tw/gdp/q", "db/tw/export/m", "db/tw/inflation/m"
    ]
    category_map = {
        "gdp": "GDP",
        "export": "Trade",
        "trade": "Trade",
        "inflation": "Inflation"
    }

    for path in db_paths:
        if not os.path.exists(path):
            continue
        split = path.split("/")
        country = split[1]
        cat = split[2]
        freq = split[3]
        all_files = os.listdir(path)
        for filename in all_files:
            # Accept either _raw.csv or _trade_m_raw.csv etc
            if filename.endswith("_raw.csv"):
                print(filename)
                new_name = filename.replace("_raw.csv", ".csv")
                print(new_name)
                raw_path = os.path.join(path, filename)
                csv_path = os.path.join(path, new_name)
                # Remove old .csv if exists
                if os.path.exists(csv_path):
                    os.remove(csv_path)
                # Map code-based category to full name expected by downstream scripts
                cat_key = cat.lower()
                cat_arg = category_map.get(cat_key, cat)
                # Run onboarding pipeline before renaming (so _raw.csv exists)
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
                # Now rename raw to .csv
                shutil.move(raw_path, csv_path)

if __name__ == "__main__":
    main()