import os

import yaml
import requests
import dotenv
import json
from distutils.version import StrictVersion

dotenv.load_dotenv()

UPDATE_ON = ["major", "minor", "patch"]
CHART_LOCATION = os.environ.get("CHART_LOCATION")

def open_chart():
    with open(CHART_LOCATION, "r") as chart:
        return yaml.safe_load(chart)


def compare_versions(current_version, latest_version):
    """Compare two versions.

    Args:
        current_version (list): The current version.
        latest_version (list): The latest version.

    Returns:
        str: The type of update.
    """
    if current_version[0] != latest_version[0]:
        return "major"
    elif current_version[1] != latest_version[1]:
        return "minor"
    elif current_version[2] != latest_version[2]:
        if "-" in latest_version[2]:
            return "pre-release"
        else:
            return "patch"


if __name__ == "__main__":
    current_chart = open_chart()
    updated_dependencies = []

    for dependency in current_chart["dependencies"]:
        print(f"Checking for updates for {dependency['name']}...")

        if dependency["repository"].startswith("https://"):
            print("Checking public repository")

            # Public repository
            public_json = requests.get(
                f'{dependency["repository"]}/index.yaml')

            if public_json.status_code == 200:
                available_versions = []
                public_json = yaml.safe_load(public_json.text)

                if "pre-release" in UPDATE_ON:
                    releases = public_json["entries"][dependency["name"]]
                else:
                    releases = [
                        release
                        for release in public_json["entries"][dependency["name"]]
                        if "-" not in release["version"]
                    ]

                latest_version = releases[0]["version"]

                print(f"Latest version: {latest_version}")

                if dependency["version"] != latest_version:

                    update_type = compare_versions(dependency["version"].split("."), latest_version.split("."))

                    if update_type in UPDATE_ON:
                        print(f"Updating {dependency['name']} to {latest_version}")
                        dependency["version"] = latest_version

                        updated_dependencies.append(dependency["name"])

                        print(f"Updating {CHART_LOCATION}")
                        with open(CHART_LOCATION, "w") as chart:
                            yaml.dump(current_chart, chart, sort_keys=False)
                else:
                    print("Running the latest version")

        if dependency["repository"].startswith("oci://"):
            print("Checking OCI registry")

            available_versions = []
            registry_address = dependency["repository"].replace(
                "oci://",
                f'https://{os.environ.get("OCI_USERNAME")}:{os.environ.get("OCI_PASSWORD")}@',
            )
            oci_response = requests.get(
                f'{registry_address}/v2/{dependency["name"]}/tags/list'
            ).text

            available_versions = json.loads(oci_response)["tags"]
            available_versions.sort(key=StrictVersion, reverse=True)

            latest_version = available_versions[0]

            update_type = compare_versions(
                dependency["version"].split("."), latest_version.split(".")
            )

            if update_type in UPDATE_ON:
                print(f"Updating {dependency['name']} to {latest_version}")
                dependency["version"] = latest_version

                updated_dependencies.append(dependency["name"])
                print(f"Updating {CHART_LOCATION}")
                with open(CHART_LOCATION, "w") as chart:
                    yaml.dump(current_chart, chart, sort_keys=False)

    if len(updated_dependencies) > 0:
        print(f"Updated dependencies: {str(updated_dependencies)}")
