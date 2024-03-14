import json
class JSONLines():
    """
    JSONLines
    format is as follows:
    a sentence of text in each line, with annotations
    
    {"text":"Google was founded on September 4, 1998, by Larry Page and Sergey Brin.","entities":[[0, 6, "ORG"],[22, 39, "DATE"],[44, 54, "PERSON"],[59, 70, "PERSON"]]}
    {"text":"Another sentence", "entities":[]}
    This is somewhat similar to WebAnno tsv format
    """
    def __init__(self):
        # Intended to consist of tuples (line, (labels))
        # Where each label is a dict {"start_offset":int,"end_offset":int,"label":"str"}
        self.lines = []
    
    def load_from_jsonlines(self, filepath):
        with open(filepath, 'r', encoding="utf-8") as inf:
            for line in inf.readlines():
                try:
                    data = json.loads(line)
                    self.lines.append(data)
                except Exception as e:
                    print(f"Exception in file {filepath}")
                    print(e)

    def write_output(self, filepath):
        with open(filepath, 'w', encoding="utf-8") as outf:
            for line in self.lines:
                line = json.dumps(line)
                outf.write("{}\n".format(line))
