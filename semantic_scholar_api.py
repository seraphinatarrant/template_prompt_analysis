import argparse
import time
from typing import List
from tqdm import tqdm

import yaml
import s2
import csv


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/semantic_graph_search.yaml',
                   help='a yaml config containing necessary API information')
    # p.add_argument('-d', dest='output_dir', default='../outputs/D4/', help='dir to write output summaries to')
    # p.add_argument('-m', dest='model_path', default='', help='path for a pre-trained embedding model')
    return p.parse_args()


def read_yaml_config(config_file):
    return yaml.load(open(config_file))

def make_row(paperID, p) -> List:
    p_full = s2.api.get_paper(paperId=p.paperId)
    authors = ";".join([a.name for a in p_full.authors])
    return [p.title, ";".join(p.intent), p.isInfluential, authors,
            p_full.abstract, p.url, p_full.doi, p_full.arxivId]


def check_rate_limit(curr_count: int, max_call: int) -> int:
    curr_count += 1
    if curr_count == max_call:
        time.sleep(300)
        curr_count = 0
    return curr_count


if __name__ == "__main__":
    args = setup_argparse()

    # print("Reading config...")
    # config = read_yaml_config(args.config_file)

    pid = "a2ce1fb96c0b78bee18bb2cb2c3d55dc48d54cbd"
    pid2 = "arXiv:1906.07337"
    pid3 = "10.18653/v1/2020.acl-main.468"

    paper = s2.api.get_paper(paperId=pid)
    paper2 = s2.api.get_paper(paperId=pid2)
    paper3 = s2.api.get_paper(paperId=pid3)

    HEADERS = ["Title", "Section", "Influential", "Authors", "Abstract", "URL", "DOI", "Arxiv"]
    citation_rows, reference_rows = [], []
    #root_paper = make_row(paper.paperId, ) TODO this will have different fields
    # Get all citations and references for a paper:
    max_call = 100
    curr_count = 1
    print(f"{len(paper.citations)} Citations")
    for c in tqdm(paper.citations):
        citation_rows.append(make_row(c.paperId, c))
        curr_count = check_rate_limit(curr_count, max_call)
    print(f"{len(paper.references)} References")
    for r in tqdm(paper.references):
        reference_rows.append(make_row(r.paperId, r))
        curr_count = check_rate_limit(curr_count, max_call)


    # then write a csv of them
    file2papers = {
        "kurita2019_citations.csv" : citation_rows,
        "kurita2019_reference.csv": reference_rows
    }
    for file, papers in file2papers.items():
        with open(file, "w", newline='') as fout:
            csvwriter = csv.writer(fout)
            csvwriter.writerow(HEADERS)
            for row in papers:
                csvwriter.writerow(row)

