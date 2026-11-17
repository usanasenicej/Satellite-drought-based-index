#!/usr/bin/env python
"""CLI helper to list and query CHIRPS precipitation pentads for Rwanda."""

import argparse
from adewi.connectors.chirps import list_pentads_for_range


def main():
    parser = argparse.ArgumentParser(description="Query CHIRPS precipitation pentads for Rwanda.")
    parser.add_argument("--start", default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2023-03-31", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    pentads = list_pentads_for_range(args.start, args.end)
    print(f"Discovered {len(pentads)} CHIRPS pentads between {args.start} and {args.end}:")
    for p in pentads[:5]:
        print(f"  [{p.year}-{p.month:02d} P{p.pentad}] -> {p.url}")
    if len(pentads) > 5:
        print(f"  ... and {len(pentads) - 5} more.")


if __name__ == "__main__":
    main()
