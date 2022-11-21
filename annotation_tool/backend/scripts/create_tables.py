import argparse

from annotation_tool.backend.models import create_tables

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create all database tables if they don't exist yet."
    )
    parser.add_argument(
        "--user",
        help="A database user identifier that should get appropriate privileges on the "
        "newly created tables.",
    )
    args = parser.parse_args()
    create_tables(args.user)
