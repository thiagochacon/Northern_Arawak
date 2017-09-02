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


csv = csv2list('raw/compiled_750.tsv', strip_lines=False, comment='>>>')
header = csv[0][5:]
D = {0: [
    'doculect', 
    'concept', 
    'concept_spanish',
    'concept_french',
    'concept_portuguese',
    'semantic_field',
    'value_in_source', 
    'value',
        'form1', 'form2', 'form', 'segments', 'source']}
idx = 1
concepts = []
cmaps = {}
for i, line in enumerate(csv[1:]):
    concept = line[0]
    spanish = line[1]
    french = line[2]
    port = line[3]
    rest = line[5:]
    cmaps[port] = concept
    semfield = line[4]
    concepts += [(str(i+1), concept, spanish, french, port, semfield)]
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
                new_line = [language, concept, 
                        spanish,
                        french,
                        port,
                        semfield,
                        cell,  
                        data.get('value', ''), data.get('form', ''),
                        data.get('phonemic', ''), form, segments, data.get('source')]
                D[idx] = [str(x) for x in new_line]
                idx += 1


csv = csv2list('raw/Baniwa_only_750', strip_lines=False)
for i, line in enumerate(csv[1:]):
    port = line[0]
    rest = [line[1]]
    concept = cmaps.get(port, '?')
    language = 'Baniwa'
    for cell in rest:
        print(cell)
        datapoints = parse_thiago(cell)
        for data in [x for x in datapoints if x]:
            form = data.get('phonemic', 
                    data.get('form', data.get('value', '')))
            if form:
                segments = ' '.join(ipa2tokens(form.replace(' ','_'), 
                        merge_vowels=False,
                        semi_diacritics = 'hsʃzʒ'))
                new_line = [language, concept, 
                        '',
                        '',
                        port,
                        '',
                        cell,  
                        data.get('value', ''), data.get('form', ''),
                        data.get('phonemic', ''), form, segments, data.get('source')]
                D[idx] = [str(x) for x in new_line]
                idx += 1


wl = Wordlist(D)

counts = defaultdict(lambda: defaultdict(list))
problematic = {}
for k, val, lang in iter_rows(wl, 'form', 'doculect'):
    try:
        tks = ipa2tokens(val, semi_diacritics='shzʃʒʂʐɕʑ', merge_vowels=False)
        cls = tokens2class(tks, 'dolgo')
        for t, c in zip(tks, cls):
            counts[lang][t, c] += [val]
        problematic[k] = ''
    except: 
        problematic[k] = '!'

for lang, vals in counts.items():
    with open(lang+'.orthography.tsv', 'w') as f:
        f.write('Grapheme\tIPA\tFREQUENCY\tEXAMPLE\n')
        for (t, c), lst in sorted(counts[lang].items(), key=lambda x: len(x[1]),
                reverse=True):
            if c != '0':
                cpart = t
            else:
                cpart = '<?>'
            print(t, c, lst)
            f.write('{0}\t{1}\t{2}\t{3}\n'.format(
                t, cpart, len(lst), lst[0]))

wl.add_entries('problematic', problematic, lambda x: x)
lex = LexStat(wl, segments='segments')
#lex.get_scorer()
lex.cluster(method='sca', threshold=0.45, ref='cogid')
lex.output('tsv', filename='wordlist-750', ignore='all', prettify=False,
        subset=True, cols=['doculect', 'concept', 
            'concept_spanish',
            'concept_french',
            'concept_portuguese',
            'semantic_field',
            'value_in_source', 'value',
        'form1', 'form2', 'form', 'segments', 'source', 'cogid', 'problematic'])


with open('concepts.tsv', 'w') as f:
    f.write('NUMBER\tENGLISH\tSPANISH\tFRENCH\tPORTUGUESE\tSEMANTIC_FIELD\n')
    for line in concepts:
        f.write('\t'.join(line)+'\n')
            


