"""Fetch and list filenames from ASF UAVSAR data directories.

Usage examples:
  python fectch_files.py --dataname SanAnd_08517_14004-009_14092-002_0153d_s01_L090_01
  python fectch_files.py --input datanames.csv
  python fectch_files.py --input datanames.json
"""

import argparse
import csv
import json
import os

import requests
from bs4 import BeautifulSoup

def get_asf_directory_filenames(url):
    """Scrape an ASF directory page and return the filenames found."""
    try:
        # Request the directory page
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        filenames = []
        # Find all <a> tags (links)
        for link in soup.find_all('a'):
            href = link.get('href')

            # Skip parent directory and navigation links
            if href and not href.startswith('/') and '?' not in href:
                # Some links might be relative or absolute; we just want the filename
                filename = href.split('/')[-1]
                if filename:
                    filenames.append(filename)

        return filenames

    except Exception as e:
        return f"Error: {e}"

def build_asf_url(dataname):
    """Build the ASF directory URL for a given dataname."""
    return f"https://uavsar.asf.alaska.edu/UA_{dataname}/"


def load_datanames_from_csv(path):
    """Load datanames from the first column of a CSV file."""
    datanames = []
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:
                continue
            dataname = row[0].strip()
            if dataname:
                datanames.append(dataname)
    return datanames


def load_datanames_from_json(path):
    """Load datanames from JSON, supporting list/dict with a dataname field."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    datanames = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                dataname = str(item.get("dataname", "")).strip()
                if dataname:
                    datanames.append(dataname)
    elif isinstance(data, dict):
        dataname = str(data.get("dataname", "")).strip()
        if dataname:
            datanames.append(dataname)
    return datanames


def resolve_datanames(args):
    """Resolve datanames from CLI args, supporting direct or file input."""
    if args.dataname:
        return [args.dataname.strip()]

    input_path = args.input
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".csv":
        return load_datanames_from_csv(input_path)
    if ext == ".json":
        return load_datanames_from_json(input_path)
    raise ValueError(f"Unsupported input file type: {ext}")


def main():
    """Parse CLI arguments and list filenames for each dataname."""
    parser = argparse.ArgumentParser(
        description="List filenames from an ASF UAVSAR directory."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--dataname",
        help="Single data name, e.g. SanAnd_08517_14004-009_14092-002_0153d_s01_L090_01",
    )
    group.add_argument(
        "--input",
        help="CSV or JSON file containing data names (CSV first column, JSON dataname field).",
    )
    args = parser.parse_args()

    datanames = resolve_datanames(args)
    if not datanames:
        print("No data names found.")
        return

    for dataname in datanames:
        asf_url = build_asf_url(dataname)
        file_list = get_asf_directory_filenames(asf_url)
        print(f"\nData name: {dataname}")
        if isinstance(file_list, list):
            print(f"Found {len(file_list)} files in directory:\n")
            for name in sorted(file_list):
                print(f" - {name}")
        else:
            print(file_list)


if __name__ == "__main__":
    main()
