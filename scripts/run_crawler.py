"""
Job Market Crawler CLI Tool
Allows executing ethical crawls across authorized feeds and simulated portals from command line.
Usage:
    python scripts/run_crawler.py --source arbeitnow --pages 3
    python scripts/run_crawler.py --source mock --pages 2
    python scripts/run_crawler.py --source remoteok --pages 2 --query python
"""

import sys
import argparse
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.engine import crawl_engine, ADAPTER_REGISTRY
from database.connection import init_db


def main():
    parser = argparse.ArgumentParser(description="Job Market Skill Demand Intelligence Crawler CLI")
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        default="mock",
        choices=list(ADAPTER_REGISTRY.keys()),
        help=f"Crawler source adapter. Available: {', '.join(ADAPTER_REGISTRY.keys())}"
    )
    parser.add_argument(
        "--pages",
        "-p",
        type=int,
        default=2,
        help="Maximum pages to crawl (default: 2)"
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default="",
        help="Optional search query filter"
    )

    args = parser.parse_args()

    print("=" * 65)
    print(" JOB MARKET INTELLIGENCE CRAWLER ENGINE ")
    print("=" * 65)
    print(f"Target Source Adapter : {args.source.upper()}")
    print(f"Max Pages to Fetch    : {args.pages}")
    if args.query:
        print(f"Search Keyword Filter : '{args.query}'")
    print("Initializing Database...")
    init_db()

    print(f"\nStarting ethical crawl run for '{args.source}'...")
    result = crawl_engine.execute_crawl(
        source_name=args.source,
        max_pages=args.pages,
        query=args.query
    )

    print("\n" + "=" * 65)
    print(" CRAWL EXECUTION SUMMARY ")
    print("=" * 65)
    for k, v in result.items():
        print(f"  {k:<22}: {v}")
    print("=" * 65)


if __name__ == "__main__":
    main()
