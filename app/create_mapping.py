import argparse

from lib.generator.mapping_generator import Mapping_Generator as MG
from lib.tools import Setting


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, required=True)
    args = parser.parse_args()

    setting = Setting()
    category_list = args.category.split(",")

    for category in category_list:
        category_full = setting.category_full_name_map[category]
        mapping_generator = MG(
            input_path=setting.category_structure[category_full]["input_path"],
            output_path=setting.category_structure[category_full]["path"],
        )

        mapping_generator.create_mapping()


if __name__ == "__main__":
    main()
