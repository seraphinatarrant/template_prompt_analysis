import argparse
import os
import time
from typing import List
from tqdm import tqdm

import yaml
import s2
import csv

HEADERS = ["Title", "Section", "Influential", "Year", "Authors", "Abstract", "URL", "DOI", "Arxiv"]


def make_row(p) -> List:
    p_full = s2.api.get_paper(paperId=p.paperId)
    authors = ";".join([a.name for a in p_full.authors])
    return [p.title, ";".join(p.intent), p.isInfluential, p.year, authors,
            p_full.abstract, p.url, p_full.doi, p_full.arxivId]


def check_rate_limit(curr_count: int, max_call: int) -> int:
    curr_count += 1
    if curr_count == max_call:
        time.sleep(300)
        curr_count = 0
    return curr_count


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='config/citation_graph.yaml',
                   help='a yaml config containing necessary API information')
    return p.parse_args()


def read_yaml_config(config_file):
    return yaml.safe_load(open(config_file))


def make_paper_reference(paper) -> str:
    first_author_name = paper.authors[0].name.split()[-1]
    return f"{first_author_name}{paper.year}"


if __name__ == "__main__":
    args = setup_argparse()

    print(f"Reading config {args.config_file}...")
    config = read_yaml_config(args.config_file)

    for pid in config["seed_paper_ids"]:
        paper = s2.api.get_paper(paperId=pid)

        citation_rows, reference_rows = [], []
        root_paper = make_paper_reference(paper)

        # Get all citations and references for a paper:
        max_call = 100
        curr_count = 1
        print(f"{len(paper.citations)} Citations")
        for c in tqdm(paper.citations):
            citation_rows.append(make_row(c))
            curr_count = check_rate_limit(curr_count, max_call)
        print(f"{len(paper.references)} References")
        for r in tqdm(paper.references):
            reference_rows.append(make_row(r))
            curr_count = check_rate_limit(curr_count, max_call)

        # write a csv of them
        file2papers = {
            os.path.join(config["output_dir"], f"{root_paper}_citations.csv"): citation_rows,
            os.path.join(config["output_dir"], f"{root_paper}_references.csv"): reference_rows
        }
        for file, papers in file2papers.items():
            with open(file, "w", newline='') as fout:
                csvwriter = csv.writer(fout)
                csvwriter.writerow(HEADERS)
                for row in papers:
                    csvwriter.writerow(row)

