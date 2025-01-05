import json
import os
import shutil
import sys
from pathlib import Path


class DataProcess:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_json()
        if not self.data:
            print(
                "File structure is incorrect! Please delete summary.json or adjust the structure!"
            )
            sys.exit(0)
        self.slug_cache = {}

    def load_json(self):
        """Load the JSON file and validate its structure, repair it if necessary"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as json_file:
                data = json.load(json_file)
            if not self.validate_json_structure(data):
                print(f"Invalid JSON structure, attempting to fix structure...")
                # Attempt to fix the structure when invalid
                if not self.fix_json_structure(data):
                    print("Structure deviation is too large to fix, program exiting")
                    sys.exit(1)
                return self.data  # Return repaired data
            return data
        else:
            try:
                print("summary.json does not exist, initializing...")
                os.makedirs(self.file_path.rstrip("summary.json"), exist_ok=True)
                shutil.copy(
                    Path(__file__).resolve().parent / "summary.json", self.file_path
                )
                with open(self.file_path, "r") as json_file:
                    data = json.load(json_file)
                if not self.validate_json_structure(data):
                    print(
                        f"Initialized summary.json has an invalid structure, fixing..."
                    )
                    if not self.fix_json_structure(data):
                        print(
                            "Structure deviation is too large to fix, program exiting"
                        )
                        sys.exit(1)
                return self.data  # Return repaired data
            except FileNotFoundError:
                print("Failed to initialize summary.json, source file does not exist")
            except OSError as e:
                print(f"Error occurred while initializing summary.json file: {e}")
        return None

    def validate_json_structure(self, data):
        """Validate if the JSON structure is as expected"""
        if (
            isinstance(data, dict)
            and "summaries" in data
            and isinstance(data["summaries"], list)
        ):
            for summary in data["summaries"]:
                if not isinstance(summary, dict):
                    return False
                required_keys = {"title", "slug", "generated", "summary", "lang"}
                if not all(key in summary for key in required_keys):
                    return False
            return True
        return False

    def fix_json_structure(self, data):
        """Attempt to fix the JSON structure by filling missing fields with default values"""
        # Check if the root structure is a dictionary
        if not isinstance(data, dict):
            print(
                "Root structure is not a dictionary, structure deviation is too large to fix"
            )
            return False
        if "summaries" not in data or not isinstance(data["summaries"], list):
            print("Missing 'summaries' field, structure deviation is too large to fix")
            return False

        # Fix each summary in the summaries list
        for summary in data["summaries"]:
            if not isinstance(summary, dict):
                print(
                    f"Invalid summary item found: {summary}, skipping repair for this item"
                )
                continue  # Skip invalid summary items

            # Fill missing fields with default values, but avoid overwriting existing fields
            if "title" not in summary:
                summary["title"] = "Untitled"
            if "slug" not in summary:
                summary["slug"] = ""
            if "generated" not in summary:
                summary["generated"] = False
            if "summary" not in summary:
                summary["summary"] = ""
            if "lang" not in summary:
                summary["lang"] = "zh"

        self.data = data  # Fix the structure by modifying the original data

        # Save the repaired data immediately after fixing the structure
        self.save_json()  # Save the changes immediately

        return True

    def check_slug_and_lang_exists(self, target_slug, target_lang):
        """Check if the slug already exists"""
        if target_slug + target_lang in self.slug_cache:
            return self.slug_cache[target_slug + target_lang]
        for summary in self.data.get("summaries", []):
            if (
                summary.get("slug") == target_slug
                and summary.get("lang") == target_lang
            ):
                self.slug_cache[target_slug + target_lang] = True
                return True
        self.slug_cache[target_slug + target_lang] = False
        return False

    def get_json_by_slug_and_lang(self, target_slug, target_lang):
        """Get the corresponding JSON data by slug"""
        for summary in self.data.get("summaries", []):
            if (
                summary.get("slug") == target_slug
                and summary.get("lang") == target_lang
            ):
                return summary
        return None

    def edit_json_by_slug_and_lang(
        self, target_slug, target_lang, new_summary, new_state
    ):
        """Edit an existing summary"""
        for summary in self.data.get("summaries", []):
            if (
                summary.get("slug") == target_slug
                and summary.get("lang") == target_lang
            ):
                summary["summary"] = new_summary
                summary["generated"] = new_state
                return None
        return None

    def save_json(self):
        """Save JSON data to the file"""
        with open(self.file_path, "w") as json_file:
            json.dump(self.data, json_file, indent=4, ensure_ascii=False)

    def add_new_summary(self, new_summary):
        """Add a new summary"""
        if "summaries" not in self.data:
            self.data["summaries"] = []
        self.data["summaries"].append(new_summary)
