#!/usr/bin/env python
# coding:utf-8
import requests
import json
import time
import mistune # markdown > html
#import tomd # html > markdown
import modified_tomd
import re

google_apikey = "<YOUR API KEY>"
args = sys.argv
source_lang = args[1]  # e.g. en
target_lang = args[2] # e.g. ja
filename = args[3] # e.g. source.ipynb
filename_translated = args[4] # e.g. target_ja.ipynb

def google_translate(original_text):
    google_translate_url = "https://translation.googleapis.com/language/translate/v2?key=" + google_apikey

    payload = {
        "q": original_text,
        "source": source_lang,
        "target": target_lang,
        "format": "html"
    }
    json_data = json.dumps(payload).encode("utf-8")
    headers = {"content-type": "application/json"}
    r = requests.post(google_translate_url, headers=headers, data=json_data)
    translated = r.json()
    return translated
  
# read ipynb and parse JSON
with open(filename, "r") as f:
  notebook = json.load(f)

# insert translated cells
new_notebook = notebook.copy()
cells = notebook["cells"].copy()
new_cells = cells.copy()
offset = 1

for index, cell in enumerate(cells):
  print("===index: " + str(index) + " offset: " + str(offset) + "===")
  
  if cell["cell_type"] == "markdown":
    print("cell: " + str(cell["source"]))
    
    original_text = "\n".join(cell["source"])
    original_html = mistune.markdown(original_text)
    r = google_translate(original_html)
    translated_html = r["data"]["translations"][0]["translatedText"]
#    translated_md = tomd.convert(translated_html)
    translated_md = modified_tomd.Tomd(translated_html).markdown
#    new_source_list = translated_md.split("\n")
    new_source_list = re.findall(".*\n", translated_md)
    new_cell = { 'cell_type': 'markdown', 'source': new_source_list }
    new_cells.insert(index + offset, new_cell)

    offset = offset + 1
    
new_notebook["cells"] = new_cells

# delete meta data
for index in range(0,len(new_notebook["cells"])):
  new_notebook["cells"][index]["metadata"] = {}
  
new_notebook["metadata"] = {}

# write .ipynb file
with open(filename_translated, "w") as f:
  json.dump(new_notebook, f, ensure_ascii=False, indent=2)