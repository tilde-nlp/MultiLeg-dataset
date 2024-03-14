import os
from jsonlines import JSONLines
from conll_2003 import Conll2003

def convert(sourcefile, trgfile):
    lines = JSONLines()
    lines.load_from_jsonlines(sourcefile)
    conllfile = Conll2003()

    for line in lines.lines:
        if len(conllfile.lines) > 0:
            conllfile.lines.append(("", ""))
        text = line['text'] 
        ents = line['label']
        curtok = ""
        inent = False
        label = "O"
        biolabel = "O"
        for pos in range(len(text)):
            for start, end, ent_label in ents:
                if end == pos:
                    if not inent:
                        print(f"File {sourcefile}")
                        print(f"Found end of entity without start. Possible overlap? Line was {line}")
                    # curtok += text[pos] 
                    if curtok:
                        conllfile.lines.append((curtok, biolabel))
                    inent = False
                    curtok = ""
                    label = "O"
                    biolabel = "O"
                if start == pos:
                    if inent: # No overlap
                        continue
                    if curtok:
                        conllfile.lines.append((curtok, biolabel))
                    curtok = ""
                    label = ent_label
                    biolabel = "B-" + label
                    inent = True

            if text[pos].isspace():
                if curtok:
                    conllfile.lines.append((curtok, biolabel))
                if label != "O":
                    biolabel = "I-" + label
                curtok = ""
                continue
            curtok += text[pos] 
        conllfile.lines.append((curtok, biolabel))
    conllfile.write_output(trgfile)

    labelfile = os.path.join(os.path.dirname(trgfile), "labels.txt")
    conllfile.update_labels_file(labelfile)
                

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('jsonlinesfolder', help='Where to get jsonlines')
    parser.add_argument('conllfolder', help='Where to put output conll')
    args = parser.parse_args()
    jsonlinesfolder = args.jsonlinesfolder
    conllfolder = args.conllfolder
    os.makedirs(conllfolder, exist_ok=True)

    for subdir, dirs, files in os.walk(jsonlinesfolder):
        for filen in files:
            if not filen.endswith(".jsonl"):
                continue
            sourcefile = subdir + os.sep + filen
            trgfile = os.path.join(conllfolder, os.path.splitext(filen)[0] + ".conll")

            convert(sourcefile, trgfile)
