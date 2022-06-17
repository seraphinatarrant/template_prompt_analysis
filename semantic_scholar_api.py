"""
Takes in yaml config specifying seed paper IDs (arxiv, DOI, semantic scholar IDs)
to look up references and citations for. Generates a citation csv and reference csv per paper,
and also a union csv that includes which seed papers voted for which references/citations.

Optionally can specify to include only influential papers or only ones referenced or cited
in certain sections (currently doesn't differentiate between references and citations though could
if useful.
"""

import argparse
import os
import time
from collections import defaultdict
from typing import List
from tqdm import tqdm

import yaml
import s2
import csv

HEADERS = ["Title", "Section", "Influential", "Year", "Authors", "Abstract", "URL", "DOI", "Arxiv"]
SUMMARY_HEADERS = ["Cites", "ReferencedBy"]


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


def check_include(p, config) -> bool:
    if config["only_influential"]:
        if not p.isInfluential:
            return False
    if config["only_include_sections"]:
        paper_sections = set(p.intent)
        if not paper_sections:  # this section is missing, so include it
            return True

        include_sections = set(config["only_include_sections"])
        if not include_sections & paper_sections:
            return False
    return True



if __name__ == "__main__":
    args = setup_argparse()

    print(f"Reading config {args.config_file}...")
    config = read_yaml_config(args.config_file)

    #TODO finish union csv
    #seed2paper_ref = defaultdict(lambda: defaultdict(list))  # for generating union, which adds columns
    #all_papers = set() # also for union csv at end

    for pid in config["seed_paper_ids"]:
        paper = s2.api.get_paper(paperId=pid)

        citation_rows, reference_rows = [], []
        root_paper = make_paper_reference(paper)

        # Get all citations and references for a paper:
        max_call = 100
        curr_count = 1
        print(f"{len(paper.citations)} Citations")
        for c in tqdm(paper.citations):
            if not check_include(c, config):
                continue
            #seed2paper_ref[c.paperID]["citation"].append(root_paper)
            #all_papers.add(c)
            citation_rows.append(make_row(c))
            curr_count = check_rate_limit(curr_count, max_call)
        print(f"{len(paper.references)} References")
        for r in tqdm(paper.references):
            if not check_include(r, config):
                continue
            #seed2paper_ref[c.paperID]["reference"].append(root_paper)
            #all_papers.add(c)
            reference_rows.append(make_row(r))
            curr_count = check_rate_limit(curr_count, max_call)

        # write a csv of them
        output_dir = config["output_dir"]
        if not os.path.exists(output_dir):
            print(f"Creating {output_dir} output path")
            os.makedirs(output_dir)
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

    # make union csv TODO





