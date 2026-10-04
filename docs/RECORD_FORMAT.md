# Record format (version 1)

One approved recipe = one file: `recipes/<slug>.json`. A worked example is in `examples/example-tomato-bruschetta.json`.
The machine-readable version is `schema/recipe.schema.json`. `tools/validate.py` enforces it and explains any problem in plain English.

## Fields
| Field | Required | Notes |
|---|---|---|
| `schema` | yes | Always `world-table-contribution/1` |
| `id` | yes | Always `community#` + slug |
| `slug` | yes | Lowercase letters, numbers, hyphens. **Must match the file name** |
| `title` | yes | 2 to 90 characters |
| `summary` | yes | One or two sentences, 10 to 300 characters |
| `country` | yes | 2-letter ISO code (`IT`, `AU`...) or **`ZZ` = World (undeclared)** |
| `category` | yes | `main` `soup` `dessert` `snack` `breakfast` `bread` `side` `salad` `sauce` `drink` |
| `difficulty` | yes | `easy` `medium` `hard` |
| `facts` | yes | `prepMinutes`, `cookMinutes` (whole numbers), `servings` (1 to 100) |
| `ingredients` | yes | List of `{quantity, unit, name, note?, scaling?, originalText?}`. See below |
| `steps` | yes | List of 1 to 40 steps, each 10 to 600 characters |
| `tags` | no | Up to 12 extra lowercase tags (ingredient words, techniques) |
| `dietsSuggested` | no | `vegetarian` `vegan` `gluten-free` `pescatarian`. **Suggestions only.** The website re-checks them and never trusts these |
| `image` | yes | `null`, or `{file, creditName?, rightsConfirmed: true}`. No photo without confirmed rights |
| `contributor` | yes | `{displayName, credit, dedication?}`. `credit: false` means shown as "community contributor" |
| `rights` | yes | `{source, confirmedAt, licence, via, evidence?, permissionNote?}` |
| `review` | yes | `{status: "approved", approvedAt, approvedBy, rulesVersions}` |
| `addedAt` | yes | Date, `YYYY-MM-DD` |

## Ingredients
- `unit` is one of: `g` `kg` `ml` `l` `tsp` `tbsp` `piece` `clove` `pinch` `sprig` `slice` `toTaste`
- For `toTaste`, `quantity` must be `null`. For every other unit it must be a number.
- Convert to these units when entering (2 cups of flour becomes grams). Keep what the person typed in `originalText` for the record.
- `scaling` is optional (`linear`, `damped`, `fixed`). If left out, the website decides.

## Rights
- `source`: `own`, `family`, or `book-or-website`. A book or website needs a `permissionNote` saying how permission was given.
- `via`: how it arrived (`form`, `facebook`, `email`). `evidence` says where, with **no links** (for example a screenshot file name).
- `licence` is always `CC-BY-SA-4.0`.

## The rules (same as the website)
English only, no links or email addresses or @handles, family-friendly. The text rules live in `rules/text-rules-v1.json`, a copy of the site's file. If the site's version changes, copy the new one over.

## Dedications and credits
The one-line `dedication` and the contributor's name appear on the recipe's page on the website. **They are not printed inside cookbooks.** A cookbook has one title and one dedication of its own, and a credits page lists contributors by name (those who set `credit: true`; the rest appear as "community contributors").

## How the website will use these (planned, not built yet)
| Here | Becomes on the site |
|---|---|
| `title`, `summary` | `title`, `summary` |
| `ingredients` | ingredient names plus detail rows (the name and note are wrapped as `{"en": ...}` like the main collection) |
| `steps` | `steps` |
| `facts` | the "Prep 20 min / Cook 45 min / 4 servings" facts |
| `country`, `category`, `difficulty`, ingredient words, `tags` | the tag row |
| verified diet labels | computed by the website's rules, **not** copied from `dietsSuggested` |
| `image.file` | the recipe image |
| `contributor`, `rights`, `review` | the provenance shown with the recipe |
