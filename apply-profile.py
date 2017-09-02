from lingpy import *
from segments.tokenizer import Tokenizer

wl = Wordlist('wordlist-750.tsv')
ops = {}
for k, lang, form, segments in iter_rows(wl, 'doculect', 'form', 'segments'):
    if lang not in ops:
        print('lang', lang)
        ops[lang] = Tokenizer(lang+'.orthography.tsv')
    wl[k, 'segments'] = ops[lang].transform(form.replace(' ', '_'), column='IPA',
            exception={"#": "#"})
wl.output('tsv', filename='wordlist-750-segmented', ignore='all')

