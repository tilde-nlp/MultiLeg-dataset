import os
from shutil import copyfile
from jsonlines import JSONLines


def _prep_head(html_file, version1, version2):
    # Prep output HTML file
    html_output = '<html>\n'
    html_output += '<head>\n'
    html_output += '<meta charset="utf-8">\n'
    html_output += '<link rel="stylesheet" href="style.css"/>\n'
    # https://api.jqueryui.com/tooltip/ JQuery tooltip widget
    html_output += '''<script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script>
        $( function() {
            $("span").tooltip({
                content: function () {
                    return $(this).prop('class') + ";  span id: " + $(this).prop('id');
                },
                items: "span[id]"
            });
        } );
    </script>'''
    html_output += '</head>\n'
    html_output += '<body>\n'
    html_output += f'<table>\n<tr>\n<th>{version1}</th>\n<th>Line No</th>\n<th>{version2}</th>\n<th>Origin</th>\n</tr>\n'
    with open(html_file, 'w', encoding="utf-8") as outf:
        outf.write(f'{html_output}')


def _prep_foot(html_file):
    html_output = '</table>\n</body>\n</html>'
    with open(html_file, 'a', encoding="utf-8") as outf:
        outf.write(f'{html_output}')


def inject_entities_into_text(text:str, entities:list) -> str:
    injected_text = ""
    for i, char in enumerate(text):
        for (start, end, label) in entities:
            if end == i:
                injected_text += f'</entity>'
        for (start, end, label) in entities:
            if start == i:
                injected_text += f'<entity class="{label}" data-toggle="tooltip" title="{label}">'
        injected_text += char
    for (start, end, label) in entities:
        if end == i + 1:
            injected_text += f'</entity>'
    return injected_text


def labels_and_number_of_labels_is_the_same(ents1:list, ents2:list) -> bool: 
    are_the_same = True
    entdic1 = {}
    entdic2 = {}
    for ent in ents1:
        old = entdic1.get(ent[2], 0)
        entdic1[ent[2]] = old + 1
    for ent in ents2:
        old = entdic2.get(ent[2], 0)
        entdic2[ent[2]] = old + 1
    for key, value in entdic1.items():
        try:
            if not entdic1[key] == entdic2[key]:
                are_the_same = False
        except KeyError:
            are_the_same = False
    for key, value in entdic2.items():
        try:
            if not entdic2[key] == entdic1[key]:
                are_the_same = False
        except KeyError:
            are_the_same = False
    return are_the_same


def compare(src_f, src_f2, out_file):
    _prep_head(out_file, src_f, src_f2)

    lines1 = JSONLines()
    lines2 = JSONLines()

    lines1.load_from_jsonlines(src_f)
    lines2.load_from_jsonlines(src_f2)

    # LEAVE ALL VISIBLE
    with open(out_file, 'a', encoding="utf-8") as outf:
        line_no = 0

        for line1, line2 in zip(lines1.lines, lines2.lines):
            line_no += 1
            text1 = line1['text']
            text2 = line2['text']
            ents1 = line1['label']
            ents2 = line2['label']

            sent1 = inject_entities_into_text(text1, ents1)
            sent2 = inject_entities_into_text(text2, ents2)

            if labels_and_number_of_labels_is_the_same(ents1, ents2):
                html_output = f'<tr class="OK"><td>{sent1}</td><td>{line_no}</td><td>{sent2}</td></tr>'
            else:
                html_output = f'<tr><td>{sent1}</td><td>{line_no}</td><td>{sent2}</td></tr>'
            outf.write(f'{html_output}')

    _prep_foot(out_file)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This is great tool!', fromfile_prefix_chars='@')
    parser.add_argument('src1_dir', help='Dircectory containing src files')
    parser.add_argument('lang1', help='Language 1')
    parser.add_argument('src2_dir', help='Dircectory containing second set of src files')
    parser.add_argument('lang2', help='Language 2')
    parser.add_argument('html_dir', help='Output file')
    args = parser.parse_args()

    src_dir1 = args.src1_dir
    src_dir2 = args.src2_dir
    lang1 = args.lang1
    lang2 = args.lang2
    html_dir = args.html_dir

    os.makedirs(html_dir, exist_ok=True)
    copyfile('style.css', os.path.join(html_dir, 'style.css'))

    # Do the comparison
    for subdir, dirs, files in os.walk(src_dir1):
        for filen in files:
            if not filen.endswith(".jsonl"):
                continue

            sourcefile1 = src_dir1 + os.sep + filen
            sourcefile2 = src_dir2 + os.sep + filen.replace(f"_{lang1}",f"_{lang2}")
            if not os.path.exists(sourcefile2):
                print(f"Second file {sourcefile2} was not found")
                sourcefile2 = src_dir2 + os.sep + filen.replace(f"_{lang1}",f"_{lang2}.unverified")
                print(f"\tTrying {sourcefile2}")
                if not os.path.exists(sourcefile2):
                    print(f"\tSecond file {sourcefile2} was not found")
                    continue

            htmlfile = filen.replace(".jsonl", ".html")
            htmlfile = os.path.join(html_dir, htmlfile)

            compare(sourcefile1, sourcefile2, htmlfile)
