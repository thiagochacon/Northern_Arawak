from lingpy import *
from collections import defaultdict

def parse_thiago(string):
    strings = ['']
    for char in string:
        strings[-1] += char
        if char == '}':
            strings += ['']
    
    dsets = []
    for string in strings:
        current = ''
        bcount = 0
        data = {}
        for char in string:
            if char == '$':
                if not current:
                    current = 'form'
                    data[current] = ''
                else:
                    current = ''
            elif char == '/':
                if not current:
                    current = 'phonemic'
                    data[current] = ''
                elif current == 'phonemic':
                    current = ''
                else:
                    data[current] += char
            elif char == '{':
                current = 'source'
                data[current] = ''
            elif char == '}':
                current = ''
            elif char == '<':
                current = 'value'
                data[current] = ''
            elif char == '(':
                bcount += 1
                if not current:
                    current = 'spanish'
                    data[current] = ''
                elif current == 'spanish':
                    data[current] += char
                else:
                    data[current] += char
            elif char == '<':
                current = 'value'
                data[current] = ''
            elif char == '>':
                current = ''
            elif char == ')':
                bcount -= 1
                if current == 'spanish' and bcount == 0:
                    current = ''
                elif current == 'spanish':
                    data[current] += char
                else:
                    data[current] += char
            elif current:
                data[current] += char
        dsets += [data]
    return dsets


csv = csv2list('arawakan.csv', strip_lines=False, comment='>>>')
header = csv[0][1:]
D = {0: ['doculect', 'concept', 'value_in_source', 'concept_spanish', 'value',
        'form1', 'form2', 'form', 'segments', 'source']}
idx = 1
for i, line in enumerate(csv[1:]):
    concept = line[0]
    rest = line[1:]
    for language, cell in zip(header, rest):
        print(cell)
        datapoints = parse_thiago(cell)
        for data in [x for x in datapoints if x]:
            form = data.get('phonemic', 
                    data.get('form', data.get('value', '')))
            if form:
                segments = ' '.join(ipa2tokens(form.replace(' ','_'), 
                        merge_vowels=False,
                        semi_diacritics = 'hsʃzʒ'))
                new_line = [language, concept, cell, data.get('spanish', ''), 
                        data.get('value', ''), data.get('form', ''),
                        data.get('phonemic', ''), form, segments, data.get('source')]
                D[idx] = [str(x) for x in new_line]
                idx += 1
wl = Wordlist(D)
lex = LexStat(wl, segments='segments')
lex.get_scorer()
lex.cluster(method='lexstat', threshold=0.6, ref='cogid')
lex.output('tsv', filename='arawakan', ignore='all', prettify=False,
        subset=True, columns=['doculect', 'concept', 'value_in_source', 'concept_spanish', 'value',
        'form1', 'form2', 'form', 'segments', 'source', 'cogid'])

            


