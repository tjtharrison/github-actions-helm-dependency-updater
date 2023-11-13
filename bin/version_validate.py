"""Script to validate versioning mode provided to GitHub action"""
import sys


def main(args):
    """
    Process provided mode and verify against accepted modes.

    Args:
        args: List of arguments provided to the script
    """

    accepted_versions = ["major", "minor", "patch", "pre-release"]

    if len(args) < 2:
        print(
            'Requires input, eg '
            '`python version_validate.py "["major","minor", "patch", "pre-release"]"`'
        )
        sys.exit(1)

    arg_list = args[1].split(",")

    for arg in arg_list:
        if arg not in accepted_versions:
            print("Provided value " + str(arg) + " not in " + str(accepted_versions))
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
