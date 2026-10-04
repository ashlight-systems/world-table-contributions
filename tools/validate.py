#!/usr/bin/env python3
"""World Table contributions: checks every recipe record.

    python3 tools/validate.py            check recipes/ and examples/
    python3 tools/validate.py --json     machine-readable output (for the Site Steward agent later)
    python3 tools/validate.py --strict   treat warnings as errors

Needs Python 3.8+ and nothing else. Exit code 0 = all good, 1 = problems found.
It checks structure and wording rules. It deliberately does NOT decide diet labels: the website
re-checks those with its own rules, and anything a contributor claims about diets is only a suggestion.
"""
import json, os, re, struct, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_RULES = json.load(open(os.path.join(ROOT, 'rules', 'text-rules-v1.json'), encoding='utf-8'))

UNITS = ['g', 'kg', 'ml', 'l', 'tsp', 'tbsp', 'piece', 'clove', 'pinch', 'sprig', 'slice', 'toTaste']
CATEGORIES = ['main', 'soup', 'dessert', 'snack', 'breakfast', 'bread', 'side', 'salad', 'sauce', 'drink']
DIFFICULTIES = ['easy', 'medium', 'hard']
DIETS = ['vegetarian', 'vegan', 'gluten-free', 'pescatarian']
SOURCES = ['own', 'family', 'book-or-website']
VIA = ['form', 'facebook', 'email']
SCALING = ['linear', 'damped', 'fixed']
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]{2,60}$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TAG = re.compile(r'^[a-z][a-z0-9-]{1,24}$')
IMG_FILE = re.compile(r'^images/[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$')
MAX_IMAGE_BYTES = 600 * 1024
WARN_IMAGE_PX = 1600

TOP_FIELDS = {'schema', 'id', 'slug', 'title', 'summary', 'country', 'category', 'difficulty', 'facts', 'ingredients', 'steps',
              'tags', 'dietsSuggested', 'image', 'contributor', 'rights', 'review', 'addedAt'}
REQUIRED = ['schema', 'id', 'slug', 'title', 'summary', 'country', 'category', 'difficulty', 'facts', 'ingredients', 'steps',
            'tags', 'image', 'contributor', 'rights', 'review', 'addedAt']

# ---- text rules (the SAME rules file the website and server read) ----
_ranges = ''.join('\\U%08x-\\U%08x' % (a, b) for a, b in TEXT_RULES['englishAllowedRanges'])
_NOT_ENGLISH = re.compile('[^' + _ranges + r'\s]')
_LINK = re.compile(TEXT_RULES['linkPattern'], re.I)
_LEET = str.maketrans(TEXT_RULES['leet'])
_BAD = set(TEXT_RULES['badWords'])

def text_problem(t):
    t = str(t or '')
    if not t.strip():
        return None
    if _NOT_ENGLISH.search(t):
        return 'is not in English (other writing systems are not accepted)'
    if _LINK.search(t):
        return 'contains a link, email address or @handle'
    if any(w in _BAD for w in re.split(r'[^a-z]+', t.lower().translate(_LEET)) if w):
        return 'is not family-friendly'
    return None

def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)

def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)

def image_size(path):
    """Width, height for JPEG/PNG using only the standard library. None if unreadable."""
    try:
        with open(path, 'rb') as f:
            head = f.read(26)
            if head[:8] == b'\x89PNG\r\n\x1a\n':
                return struct.unpack('>II', head[16:24])
            if head[:2] == b'\xff\xd8':
                f.seek(2)
                while True:
                    b = f.read(1)
                    while b and b != b'\xff':
                        b = f.read(1)
                    while b == b'\xff':
                        b = f.read(1)
                    if not b:
                        return None
                    m = b[0]
                    if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                        continue
                    n = struct.unpack('>H', f.read(2))[0]
                    if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        data = f.read(5)
                        h, w = struct.unpack('>HH', data[1:5])
                        return (w, h)
                    f.seek(n - 2, 1)
    except Exception:
        return None
    return None

def check_record(rec, filename, root):
    """Returns (errors, warnings), each a list of plain-English strings."""
    E, W = [], []
    if not isinstance(rec, dict):
        return ['the file must contain one JSON object'], W
    for k in REQUIRED:
        if k not in rec:
            E.append("missing required field '%s'" % k)
    for k in rec:
        if k not in TOP_FIELDS:
            E.append("unknown field '%s' (check the spelling, or see docs/RECORD_FORMAT.md)" % k)
    if E and any(m.startswith('missing') for m in E):
        return E, W

    def s(k, lo, hi):
        v = rec.get(k)
        if not isinstance(v, str) or not (lo <= len(v.strip()) <= hi):
            E.append("'%s' must be text between %d and %d characters" % (k, lo, hi))
            return None
        return v

    if rec['schema'] != 'world-table-contribution/2':
        E.append("'schema' must be exactly world-table-contribution/2")
    slug = rec['slug']
    if not isinstance(slug, str) or not SLUG.match(slug):
        E.append("'slug' must be lowercase letters, numbers and hyphens, 3 to 61 characters")
    else:
        if filename != slug + '.json':
            E.append("file name must be '%s.json' to match the slug (it is '%s')" % (slug, filename))
        if rec['id'] != 'community#' + slug:
            E.append("'id' must be 'community#%s'" % slug)
    s('title', 2, 90); s('summary', 10, 300)
    if not (isinstance(rec['country'], str) and re.match(r'^[A-Z]{2}$', rec['country'])):
        E.append("'country' must be a 2-letter ISO code like IT or AU, or ZZ for World (undeclared)")
    if rec['category'] not in CATEGORIES:
        E.append("'category' must be one of: " + ', '.join(CATEGORIES))
    if rec['difficulty'] not in DIFFICULTIES:
        E.append("'difficulty' must be easy, medium or hard")

    f = rec['facts']
    if not isinstance(f, dict) or set(f) != {'prepMinutes', 'cookMinutes', 'servings'}:
        E.append("'facts' must have exactly prepMinutes, cookMinutes and servings")
    else:
        for k, lo, hi in (('prepMinutes', 0, 1440), ('cookMinutes', 0, 1440), ('servings', 1, 100)):
            if not is_int(f[k]) or not (lo <= f[k] <= hi):
                E.append("facts.%s must be a whole number from %d to %d" % (k, lo, hi))

    ing = rec['ingredients']
    if not isinstance(ing, list) or not (2 <= len(ing) <= 60):
        E.append("'ingredients' must be a list of 2 to 60 items")
    else:
        for n, row in enumerate(ing, 1):
            tag = 'ingredient %d' % n
            if not isinstance(row, dict):
                E.append(tag + ' must be an object'); continue
            for k in row:
                if k not in ('quantity', 'unit', 'name', 'note', 'scaling', 'originalText'):
                    E.append("%s has an unknown field '%s'" % (tag, k))
            for k in ('quantity', 'unit', 'name'):
                if k not in row:
                    E.append("%s is missing '%s'" % (tag, k))
            if 'unit' in row and row['unit'] not in UNITS:
                E.append("%s: unit '%s' is not allowed. Use one of: %s" % (tag, row['unit'], ', '.join(UNITS)))
            q = row.get('quantity', 0)
            if row.get('unit') == 'toTaste':
                if q is not None:
                    E.append(tag + ": quantity must be null when the unit is toTaste")
            elif not is_num(q) or q < 0:
                E.append(tag + ": quantity must be a number (or null only for toTaste)")
            nm = row.get('name')
            if not isinstance(nm, str) or not (2 <= len(nm.strip()) <= 80):
                E.append(tag + ": name must be 2 to 80 characters")
            if 'note' in row and (not isinstance(row['note'], str) or len(row['note']) > 120):
                E.append(tag + ": note must be text up to 120 characters")
            if 'scaling' in row and row['scaling'] not in SCALING:
                E.append(tag + ": scaling must be linear, damped or fixed (or leave it out)")
            for k in ('name', 'note', 'originalText'):
                if isinstance(row.get(k), str):
                    p = text_problem(row[k])
                    if p: E.append("%s %s %s" % (tag, k, p))

    st = rec['steps']
    if not isinstance(st, list) or not (1 <= len(st) <= 40):
        E.append("'steps' must be a list of 1 to 40 steps")
    else:
        if len(st) == 1:
            W.append('only one method step. Most recipes read better split into several')
        for n, x in enumerate(st, 1):
            if not isinstance(x, str) or not (10 <= len(x.strip()) <= 600):
                E.append('step %d must be 10 to 600 characters' % n)
            else:
                p = text_problem(x)
                if p: E.append('step %d %s' % (n, p))

    tags = rec.get('tags', [])
    if not isinstance(tags, list) or not (2 <= len(tags) <= 12) or len(set(map(str, tags))) != len(tags):
        E.append("'tags' must be a list of 2 to 12 different tags")
    else:
        for t in tags:
            if not isinstance(t, str) or not TAG.match(t):
                E.append("tag '%s' must be lowercase letters, numbers or hyphens" % t)
    ds = rec.get('dietsSuggested', [])
    if not isinstance(ds, list) or any(d not in DIETS for d in ds) or len(set(map(str, ds))) != len(ds):
        E.append("'dietsSuggested' may only contain: " + ', '.join(DIETS))

    for k in ('title', 'summary'):
        if isinstance(rec.get(k), str):
            p = text_problem(rec[k])
            if p: E.append("'%s' %s" % (k, p))

    img = rec.get('image')
    if img is not None:
        if not isinstance(img, dict) or set(img) - {'file', 'alt', 'creditName', 'rightsConfirmed'}:
            E.append("'image' must be null, or have only file, alt, creditName and rightsConfirmed")
        else:
            if img.get('rightsConfirmed') is not True:
                E.append('image.rightsConfirmed must be true. Without that, publish the recipe without its photo (use "image": null)')
            alt = img.get('alt')
            if not isinstance(alt, str) or not (5 <= len(alt.strip()) <= 160):
                E.append('image.alt must be 5 to 160 characters of plain-language image description')
            else:
                p = text_problem(alt)
                if p: E.append('image.alt ' + p)
            fl = img.get('file')
            if not isinstance(fl, str) or not IMG_FILE.match(fl):
                E.append("image.file must look like images/your-slug.jpg (jpg, jpeg, png or webp)")
            else:
                path = os.path.join(root, fl)
                if not os.path.isfile(path):
                    E.append("image file '%s' was not found" % fl)
                else:
                    size = os.path.getsize(path)
                    if size > MAX_IMAGE_BYTES:
                        E.append("image is %d KB. Please shrink it to under %d KB" % (size // 1024, MAX_IMAGE_BYTES // 1024))
                    dim = image_size(path)
                    if dim and max(dim) > WARN_IMAGE_PX:
                        W.append('image is %dx%d. Pictures over %d px on the long side are larger than needed' % (dim[0], dim[1], WARN_IMAGE_PX))
            if isinstance(img.get('creditName'), str):
                p = text_problem(img['creditName'])
                if p: E.append('image.creditName ' + p)

    c = rec['contributor']
    if not isinstance(c, dict) or set(c) - {'displayName', 'credit', 'dedication'} or 'displayName' not in c or 'credit' not in c:
        E.append("'contributor' needs displayName and credit (and optionally dedication)")
    else:
        if not isinstance(c['displayName'], str) or not (1 <= len(c['displayName'].strip()) <= 60):
            E.append('contributor.displayName must be 1 to 60 characters')
        if not isinstance(c['credit'], bool):
            E.append('contributor.credit must be true or false')
        if 'dedication' in c and (not isinstance(c['dedication'], str) or len(c['dedication']) > 140):
            E.append('contributor.dedication must be text up to 140 characters')
        for k in ('displayName', 'dedication'):
            if isinstance(c.get(k), str):
                p = text_problem(c[k])
                if p: E.append('contributor.%s %s' % (k, p))

    r = rec['rights']
    if not isinstance(r, dict) or set(r) - {'source', 'confirmedAt', 'licence', 'via', 'evidence', 'permissionNote', 'sourceTitle', 'sourceUrl'}:
        E.append("'rights' has missing or unknown fields")
    else:
        if r.get('source') not in SOURCES: E.append('rights.source must be: ' + ', '.join(SOURCES))
        if r.get('via') not in VIA: E.append('rights.via must be: ' + ', '.join(VIA))
        if r.get('licence') != 'CC-BY-SA-4.0': E.append("rights.licence must be 'CC-BY-SA-4.0'")
        if not (isinstance(r.get('confirmedAt'), str) and valid_date(r['confirmedAt'])): E.append('rights.confirmedAt must be a date like 2026-10-03')
        if r.get('source') == 'book-or-website' and not str(r.get('permissionNote', '')).strip():
            E.append("a recipe from a book or website needs rights.permissionNote saying how permission was given")
        for k in ('evidence', 'permissionNote', 'sourceTitle'):
            if isinstance(r.get(k), str):
                p = text_problem(r[k])
                if p: E.append('rights.%s %s' % (k, p))
        if 'sourceUrl' in r:
            u = r.get('sourceUrl')
            if not isinstance(u, str) or not re.match(r'^https://[^\s]{3,240}$', u) or len(u) > 250:
                E.append('rights.sourceUrl must be a Director-reviewed HTTPS URL up to 250 characters')

    rv = rec['review']
    if not isinstance(rv, dict) or set(rv) - {'status', 'approvedAt', 'approvedBy', 'rulesVersions', 'submissionId'} or any(k not in rv for k in ('status', 'approvedAt', 'approvedBy', 'rulesVersions')):
        E.append("'review' needs status, approvedAt, approvedBy and rulesVersions")
    else:
        if rv['status'] != 'approved': E.append("review.status must be 'approved'. Only approved recipes belong in this repository")
        if not (isinstance(rv['approvedAt'], str) and valid_date(rv['approvedAt'])): E.append('review.approvedAt must be a date like 2026-10-03')
        if not isinstance(rv['approvedBy'], str) or not rv['approvedBy'].strip(): E.append('review.approvedBy must be filled in')
        if not isinstance(rv['rulesVersions'], dict): E.append('review.rulesVersions must be an object')
        if 'submissionId' in rv and (not isinstance(rv['submissionId'], str) or not re.match(r'^WT-SUB-[A-Z0-9-]{6,64}$', rv['submissionId'])):
            E.append("review.submissionId must look like WT-SUB-...")
    if not (isinstance(rec['addedAt'], str) and valid_date(rec['addedAt'])):
        E.append("'addedAt' must be a date like 2026-10-03")
    return E, W

def valid_date(s):
    if not DATE.match(s):
        return False
    try:
        datetime.date.fromisoformat(s); return True
    except ValueError:
        return False

def validate_tree(root=ROOT, folders=('recipes', 'examples')):
    results, seen_slugs, seen_titles = [], {}, {}
    for folder in folders:
        d = os.path.join(root, folder)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.json'):
                continue
            path = os.path.join(folder, fn)
            try:
                rec = json.load(open(os.path.join(d, fn), encoding='utf-8'))
            except Exception as e:
                results.append({'file': path, 'errors': ['could not read the file as JSON: %s' % e], 'warnings': []}); continue
            errors, warnings = check_record(rec, fn, root)
            if isinstance(rec, dict) and folder == 'recipes':
                sl = rec.get('slug'); ti = str(rec.get('title', '')).strip().lower()
                if sl in seen_slugs: errors.append("duplicate slug (also used by %s)" % seen_slugs[sl])
                seen_slugs.setdefault(sl, path)
                if ti and ti in seen_titles: warnings.append("same title as %s. Is it a duplicate?" % seen_titles[ti])
                seen_titles.setdefault(ti, path)
            results.append({'file': path, 'errors': errors, 'warnings': warnings})
    return results

def main(argv):
    strict = '--strict' in argv
    results = validate_tree()
    if '--json' in argv:
        print(json.dumps({'rulesVersion': TEXT_RULES['version'], 'results': results}, indent=1))
    else:
        print('World Table contributions: checking with text rules v%s\n' % TEXT_RULES['version'])
        for r in results:
            mark = 'OK  ' if not r['errors'] else 'FAIL'
            print('%s %s' % (mark, r['file']))
            for e in r['errors']: print('       problem: ' + e)
            for w in r['warnings']: print('       note:    ' + w)
        bad = sum(1 for r in results if r['errors'])
        notes = sum(len(r['warnings']) for r in results)
        print('\n%d file(s) checked, %d with problems, %d note(s).' % (len(results), bad, notes))
        if not results:
            print('(No recipe files yet. That is fine for a new repository.)')
    bad = any(r['errors'] for r in results) or (strict and any(r['warnings'] for r in results))
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
