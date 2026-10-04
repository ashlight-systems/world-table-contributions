# Record format (version 2)

One **approved** recipe = one file: `recipes/<slug>.json`. A worked example is in `examples/example-tomato-bruschetta.json`.
The machine-readable contract is `schema/recipe.schema.json`. `tools/validate.py` enforces the repository rules in plain English.

Version 2 is the first form-ready approved record. It preserves the V1 vocabulary while making three decisions explicit:
**country is required, a recipe needs at least two ingredients, and an approved recipe needs at least two subject tags.**

## Fields
| Field | Required | Notes |
|---|---|---|
| `schema` | yes | Always `world-table-contribution/2` |
| `id` | yes | Always `community#` + slug |
| `slug` | yes | Lowercase letters, numbers, hyphens. **Must match the file name** |
| `title` | yes | 2 to 90 characters |
| `summary` | yes | The recipe intro shown on the site, 10 to 300 characters |
| `country` | yes | 2-letter ISO code (`IT`, `AU`...) or **`ZZ` = World / multiple or undeclared origin** |
| `category` | yes | `main` `soup` `dessert` `snack` `breakfast` `bread` `side` `salad` `sauce` `drink` |
| `difficulty` | yes | `easy` `medium` `hard` |
| `facts` | yes | `prepMinutes`, `cookMinutes`, `servings` |
| `ingredients` | yes | **2 to 60** structured ingredient rows |
| `steps` | yes | 1 to 40 method steps, each 10 to 600 characters |
| `tags` | yes | **2 to 12** accepted subject tags. Country/category/difficulty do not count |
| `dietsSuggested` | no | Suggestions only. The website re-checks diets independently |
| `image` | yes | `null`, or `{file, alt, creditName?, rightsConfirmed: true}` |
| `contributor` | yes | `{displayName, credit, dedication?}` |
| `rights` | yes | provenance and permission record; approved source title/URL may be added by the Director |
| `review` | yes | approved decision, rule versions, optional private-submission receipt ID |
| `addedAt` | yes | `YYYY-MM-DD` |

## Ingredients
Each ingredient is `{quantity, unit, name, note?, scaling?, originalText?}`.
- `unit`: `g` `kg` `ml` `l` `tsp` `tbsp` `piece` `clove` `pinch` `sprig` `slice` `toTaste`
- `toTaste` uses `quantity: null`; every other unit needs a number.
- The form can retain what the contributor typed in `originalText` while normalising the public row.
- `scaling` is optional: `linear`, `damped`, `fixed`.

## Tags
The contribution form should suggest tags **after ingredients have been committed**, because that is when the form has enough information to help.
The contributor can accept/remove suggestions before preview. The approved record must contain at least two meaningful tags.
Country, category and difficulty are already first-class fields and do not consume the two-tag minimum.

## Images
The form should prepare the image **before** it reaches Git:
- recommended presentation: **4:3**
- recommended working size: about **1600 × 1200 px**
- JPG, PNG or WebP
- crop/resize/compress client-side where possible
- contributor must confirm rights
- `alt` text is required for an approved image
- repository validator currently limits the final file to 600 KB and notes images larger than 1600 px on the long side

## Rights
`source` remains `own`, `family`, or `book-or-website`.
A book/website source requires `permissionNote`. After Director review, the approved record may also carry `sourceTitle` and an HTTPS `sourceUrl`.
Raw contributor text still cannot contain links, email addresses or social handles.

## Review
Only **approved** records belong in this repository. A public form submission is not an approved Git record.
`review.submissionId` may link the approved record to the private moderation receipt without publishing the private moderation data itself.

## Planned form → Git boundary
The public website form creates a **private pending submission**, not a Git recipe:

`public form → private moderation record → Director approval → world-table-contribution/2 → Git → pinned website build`

That separation prevents a user from creating an `approved` Git record themselves.

## Website mapping
The World Table can map V2 directly:
- `title`, `summary`, `country`, `category`, `difficulty`, `facts`
- structured `ingredients` and `steps`
- verified tags and separately re-computed diet labels
- optional prepared image
- contributor/provenance/review metadata
