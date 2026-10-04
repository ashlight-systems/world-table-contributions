#!/usr/bin/env python3
"""Tests the checker itself: breaks a good recipe in many ways and confirms each is caught.
    python3 tools/test_validate.py
Uses only the standard library."""
import copy, json, os, shutil, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate

ROOT = validate.ROOT
GOOD = json.load(open(os.path.join(ROOT, 'examples', 'example-tomato-bruschetta.json'), encoding='utf-8'))
passed = failed = 0

def run(name, mutate, expect=None, filename=None, files=None, warn=None):
    """expect=None means 'must be clean'. expect='text' means an error containing that text."""
    global passed, failed
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, 'recipes')); os.makedirs(os.path.join(tmp, 'images')); os.makedirs(os.path.join(tmp, 'rules'))
        shutil.copy(os.path.join(ROOT, 'rules', 'text-rules-v1.json'), os.path.join(tmp, 'rules'))
        rec = copy.deepcopy(GOOD)
        if mutate: mutate(rec, tmp)
        fn = filename or (rec.get('slug', 'x') + '.json' if isinstance(rec, dict) else 'x.json')
        json.dump(rec, open(os.path.join(tmp, 'recipes', fn), 'w', encoding='utf-8'))
        for extra in (files or []):
            json.dump(extra[1], open(os.path.join(tmp, 'recipes', extra[0]), 'w', encoding='utf-8'))
        res = validate.validate_tree(tmp, folders=('recipes',))
        errs = [e for r in res for e in r['errors']]; warns = [w for r in res for w in r['warnings']]
        if expect is None and warn is None:
            ok = not errs
        elif expect is None:
            ok = not errs and any(warn in w for w in warns)
        else:
            ok = any(expect in e for e in errs)
        if ok: passed += 1; print('PASS', name)
        else: failed += 1; print('FAIL', name, '| errors:', errs[:3], '| warnings:', warns[:2])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def setp(path, value):
    def f(rec, tmp):
        o = rec
        for k in path[:-1]: o = o[k]
        o[path[-1]] = value
    return f
def delete(key): return lambda rec, tmp: rec.pop(key)

run('the good example is clean', None)
# --- structure ---
run('missing a required field', delete('summary'), "missing required field 'summary'")
run('unknown top-level field (typo)', lambda r, t: r.update({'sumary': 'x'}), "unknown field 'sumary'")
run('file name must match the slug', None, "file name must be", filename='something-else.json')
run('id must be community#slug', setp(['id'], 'community#other-name'), "'id' must be")
run('slug with capitals or spaces', lambda r, t: r.update({'slug': 'Bad Slug'}), "'slug' must be")
run('wrong schema tag', setp(['schema'], 'something/2'), "'schema' must be exactly")
# --- vocabularies ---
run('country must be a code, not a name', setp(['country'], 'Italy'), "'country' must be a 2-letter")
run('ZZ (World undeclared) is allowed', setp(['country'], 'ZZ'), None)
run('unknown category', setp(['category'], 'brunch'), "'category' must be one of")
run('unknown difficulty', setp(['difficulty'], 'tricky'), "'difficulty' must be")
run('unit not in the allowed list', lambda r, t: r['ingredients'][0].update({'unit': 'cup'}), "unit 'cup' is not allowed")
run('quantity must be null for toTaste', lambda r, t: r['ingredients'][-1].update({'quantity': 1}), 'must be null when the unit is toTaste')
run('quantity cannot be null for grams', lambda r, t: r['ingredients'][0].update({'quantity': None}), 'quantity must be a number')
run('negative quantity', lambda r, t: r['ingredients'][0].update({'quantity': -2}), 'quantity must be a number')
run('bad scaling value', lambda r, t: r['ingredients'][0].update({'scaling': 'huge'}), 'scaling must be')
run('facts must be whole numbers', setp(['facts', 'servings'], 2.5), 'facts.servings')
run('servings cannot be zero', setp(['facts', 'servings'], 0), 'facts.servings')
run('steps cannot be empty', setp(['steps'], []), "'steps' must be a list")
run('a step that is too short', setp(['steps'], ['Mix.']), 'step 1 must be')
run('diet suggestion outside the list', setp(['dietsSuggested'], ['keto']), "'dietsSuggested' may only contain")
run('tag with capitals', setp(['tags'], ['Tomato']), "tag 'Tomato'")
run('too many tags', setp(['tags'], ['t%02d' % i for i in range(13)]), "'tags' must be a list")
run('bad date', setp(['addedAt'], '3/10/2026'), "'addedAt' must be a date")
run('impossible date', setp(['addedAt'], '2026-13-45'), "'addedAt' must be a date")
# --- text rules (shared with the website and server) ---
run('non-English title', setp(['title'], 'Борщ домашний'), 'is not in English')
run('accented English text is fine', setp(['summary'], 'Crème fraîche and jalapeño on toasted bread, a café classic.'), None)
run('link inside a step', setp(['steps'], ['Serve with the sauce from www.example.com for best results.']), 'contains a link')
run('email address in the summary', setp(['summary'], 'Ask me at jane@example.com for the story behind this dish.'), 'contains a link')
run('profanity in the dedication', lambda r, t: r['contributor'].update({'dedication': 'what the sh1t'}), 'not family-friendly')
run('non-English display name', lambda r, t: r['contributor'].update({'displayName': 'Привет'}), 'is not in English')
run('emoji in text is fine', lambda r, t: r['contributor'].update({'dedication': 'For Nanna 🍰'}), None)
# --- images and rights ---
def with_image(size=2000, confirmed=True, name='example-tomato-bruschetta.jpg', create=True):
    def f(rec, tmp):
        if create:
            open(os.path.join(tmp, 'images', name), 'wb').write(b'\xff\xd8' + b'0' * size)
        rec['image'] = {'file': 'images/' + name, 'rightsConfirmed': confirmed, 'creditName': 'Example Contributor'}
    return f
run('image with rights confirmed is fine', with_image(), None)
run('image without rights confirmation', with_image(confirmed=False), 'rightsConfirmed must be true')
run('image file is missing', with_image(create=False), 'was not found')
run('image over the size limit', with_image(size=700 * 1024), 'Please shrink it')
run('image path outside images/', lambda r, t: r.update({'image': {'file': '../secret.jpg', 'rightsConfirmed': True}}), 'image.file must look like')
run('recipe from a book/website needs a permission note', lambda r, t: r['rights'].update({'source': 'book-or-website'}), 'needs rights.permissionNote')
run('book/website with a permission note is fine', lambda r, t: r['rights'].update({'source': 'book-or-website', 'permissionNote': 'Author emailed permission in writing.'}), None)
run('wrong licence', lambda r, t: r['rights'].update({'licence': 'All-rights-reserved'}), "rights.licence must be")
run('only approved recipes belong here', lambda r, t: r['review'].update({'status': 'pending'}), "review.status must be 'approved'")
run('credit must be true or false', lambda r, t: r['contributor'].update({'credit': 'yes'}), 'contributor.credit must be true or false')
run('credit false with a dedication is allowed', lambda r, t: r['contributor'].update({'credit': False}), None)
# --- across files ---
dup = copy.deepcopy(GOOD); dup['slug'] = 'another-one'; dup['id'] = 'community#another-one'
run('same title in two files is only a note', None, None, files=[('another-one.json', dup)], warn='same title as')
# --- a broken file ---
def broken(rec, tmp): pass
tmpd = tempfile.mkdtemp(); os.makedirs(os.path.join(tmpd, 'recipes')); os.makedirs(os.path.join(tmpd, 'rules'))
shutil.copy(os.path.join(ROOT, 'rules', 'text-rules-v1.json'), os.path.join(tmpd, 'rules'))
open(os.path.join(tmpd, 'recipes', 'oops.json'), 'w').write('{ "title": "missing a bracket" ')
res = validate.validate_tree(tmpd, folders=('recipes',)); shutil.rmtree(tmpd)
if res and 'could not read the file as JSON' in res[0]['errors'][0]: passed += 1; print('PASS a file that is not valid JSON gets a clear message')
else: failed += 1; print('FAIL invalid JSON handling', res)
# --- an empty repository is fine ---
tmpe = tempfile.mkdtemp(); os.makedirs(os.path.join(tmpe, 'recipes')); os.makedirs(os.path.join(tmpe, 'rules'))
shutil.copy(os.path.join(ROOT, 'rules', 'text-rules-v1.json'), os.path.join(tmpe, 'rules'))
if validate.validate_tree(tmpe) == []: passed += 1; print('PASS a brand-new repository with no recipes is not an error')
else: failed += 1; print('FAIL empty repository')
shutil.rmtree(tmpe)
print('\nVALIDATOR TESTS: %d passed, %d failed' % (passed, failed))
sys.exit(1 if failed else 0)
