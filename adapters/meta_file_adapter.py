from ports.output_port import MetaFilePort
import json


class MetaFileAdapter(MetaFilePort):
    def get_meta_data(self, meta_file) -> dict:
        try:
            with open(meta_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Meta file contains incorrect JSON.")
        #check data type from meta file (dict)
        if not isinstance(data, dict):
            raise ValueError("Incorrect meta file data type.")
        
        return data
    
    def save_meta_data(self, meta_file, meta_data: dict) -> None:
        with open(meta_file, "w", encoding="utf=8") as f:
            json.dump(meta_data, f, indent=4, ensure_ascii=False)