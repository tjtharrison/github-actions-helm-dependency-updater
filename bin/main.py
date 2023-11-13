"""Script to be used by GitHub action to update chart dependencies."""
import json
import os
from distutils.version import StrictVersion

import dotenv
import requests
import yaml

dotenv.load_dotenv()

UPDATE_ON = ["major", "minor", "patch"]
CHART_LOCATION = os.environ.get("CHART_LOCATION")


def open_chart():
    """Open the chart.

    Returns:
        dict: The chart.
    """
    with open(CHART_LOCATION, "r", encoding="UTF-8") as current_chart_file:
        return yaml.safe_load(current_chart_file)


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
                f'{dependency["repository"]}/index.yaml',
                timeout=10
            )

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
                    UPDATE_TYPE = compare_versions(
                        dependency["version"].split("."), latest_version.split(".")
                    )

                    if UPDATE_TYPE in UPDATE_ON:
                        print(f"Updating {dependency['name']} to {latest_version}")
                        dependency["version"] = latest_version

                        updated_dependencies.append(dependency["name"])

                        print(f"Updating {CHART_LOCATION}")
                        with open(CHART_LOCATION, "w", encoding="UTF-8") as chart_file:
                            yaml.dump(current_chart, chart_file, sort_keys=False)
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
                f'{registry_address}/v2/{dependency["name"]}/tags/list',
                timeout=10
            ).text

            available_versions = json.loads(oci_response)["tags"]
            available_versions.sort(key=StrictVersion, reverse=True)

            latest_version = available_versions[0]

            UPDATE_TYPE = compare_versions(
                dependency["version"].split("."), latest_version.split(".")
            )

            if UPDATE_TYPE in UPDATE_ON:
                print(f"Updating {dependency['name']} to {latest_version}")
                dependency["version"] = latest_version

                updated_dependencies.append(dependency["name"])
                print(f"Updating {CHART_LOCATION}")
                with open(CHART_LOCATION, "w", encoding="UTF-8") as chart:
                    yaml.dump(current_chart, chart, sort_keys=False)

    if len(updated_dependencies) > 0:
        print(f"Updated dependencies: {str(updated_dependencies)}")
