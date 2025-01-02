import os
import argparse
from pathlib import Path
from glob import glob

def get_test_files(test_dir="tests"):
    """Retrieve all test files from the test directory."""
    # return sorted(Path(test_dir).rglob("test_*.py"))
    return sorted(glob("tests" + "/**/" + "test_*.py", recursive=True))

def split_tests(test_files, group, total_groups):
    """Split test files into groups."""
    return [file for i, file in enumerate(test_files) if i % total_groups == group - 1]

def main():
    parser = argparse.ArgumentParser(description="Split test files for parallel execution.")
    parser.add_argument("--group", type=int, required=True, help="Group number (1-indexed).")
    parser.add_argument("--total-groups", type=int, required=True, help="Total number of groups.")
    parser.add_argument("--test-dir", default="tests", help="Directory containing test files.")

    args = parser.parse_args()
    test_files = get_test_files(args.test_dir)
    print(f"{test_files=}")
    group_files = split_tests(test_files, args.group, args.total_groups)
    print(f"{group_files=}")

    if not group_files:
        print(f"No tests to run for group {args.group}")
    else:
        # Write the list of test files to a text file for pytest to use
        with open("test_files.txt", "w") as f:
            for file in group_files:
                f.write(f"{file}\n")

if __name__ == "__main__":
    main()
