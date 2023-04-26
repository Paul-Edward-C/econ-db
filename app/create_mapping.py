from lib.tools import Setting
from lib.mapping_generator import Mapping_generator as MG


def main():
    setting = Setting()
    category_list = list(setting.category_structure.keys())
    
    for category in category_list:
        mapping_generator = MG(input_path=setting.category_structure[category]["input_path"],
                               output_path=setting.category_structure[category]["path"])
    
    
if __name__ == "__main__":
    main()