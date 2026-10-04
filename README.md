# World Table contributions

Recipes contributed by the community to **The World Table** (https://www.ashlightsystems.com.au/recipes/).

The main collection of 501 recipes comes from a separate, pinned source repository. **This repository holds everything added after that**:
recipes that people share, reviewed and approved by the Director, with who contributed them and why we are allowed to publish them.

## What is here
| Folder | What it holds |
|---|---|
| `recipes/` | **Approved** recipes, one JSON file each (`recipes/<slug>.json`). Only approved recipes go here. |
| `images/` | Photos for those recipes, only where the contributor confirmed they own the photo. |
| `examples/` | A worked example of the record format. Not published. |
| `schema/` | The approved-record JSON Schema (currently `world-table-contribution/2`). |
| `rules/` | A copy of the site's text rules (English only, no links, family-friendly). |
| `tools/` | `validate.py` checks every recipe. `test_validate.py` tests the checker itself. |
| `docs/` | `GIT_FIRST_TIME.md` (start here if Git is new to you) and `RECORD_FORMAT.md`. |

## Rights and licences
This repository can contain more than one legitimate rights path.

- Original community recipes normally use **CC BY-SA 4.0**.
- Licensed-source recipes preserve the **source licence or explicit permission** recorded in that recipe's `rights` block.
- `UNKNOWN` rights may exist in private moderation, but **never** in this approved Git repository.
- Photographs retain their recorded source/owner rights and are included only after review.

Always read the individual recipe record before reusing sourced material; a repository-wide licence does not override a recipe's recorded source licence.

## How a recipe gets here
1. Someone shares a recipe (the website form when it exists, or a Facebook comment until then).
2. The Director reviews it, assigns tags and resolves the rights/licence.
3. The approved record is saved in `recipes/` and any photo in `images/`.
4. The website build reads this repository at a specific **commit** (like a numbered snapshot) so every published page can be traced back to exactly what was approved.

## Rules of the house
- **Add, don't rewrite.** Fix mistakes with a new commit. Never rewrite or delete history, because the website points at specific commits.
- **No private data.** No IP addresses, emails, passwords or anything from the admin. Only what is meant to be public.
- **Run the checker** (or let GitHub do it: see `docs/GIT_FIRST_TIME.md`) before relying on a change.

## Status
Repository and validation workflow are live. Contribution schema V2 is the form-ready approved-record contract. The public Add a Recipe form and the build step that merges approved recipes into the website are the next pieces.
