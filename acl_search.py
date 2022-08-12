from anthology import Anthology

social_terms = ["social","stereotype","harm","gender","ethnicity","race","bias","raci","sexi","toxic"]

'''
with open("acl_search_output.txt","w") as f:
    anthology = Anthology(importdir='acl-anthology/data')
    for id_, paper in anthology.papers.items():
        abstract = paper.get_abstract('text')
        #if ("prompt" in abstract) or ("trigger" in abstract):
        if True:
            if ("generat" in abstract) or ("NLG" in abstract) or ("language model" in abstract) or ("LM" in abstract):
                if any(x in abstract for x in social_terms):
                    #f.write(f"{paper.get_title('text')},{paper.anthology_id}\n")
                    f.write(f"{paper.as_bibtex()}\n")

''' 
