# World Table recipe form pipeline V2

The public **Add a Recipe** form is a submission tool, not a Git editor.

## Proposed steps
1. **Recipe identity** — title, intro, country (required), category, difficulty, prep/cook/servings.
2. **Ingredients** — structured rows; minimum 2.
3. **Smart classification** — suggest ingredient/technique tags from what was entered; contributor confirms at least 2.
4. **Method** — numbered, reorderable steps.
5. **Photo** — optional; 4:3 preview, crop, resize/compress, rights confirmation, alt text.
6. **Contributor & rights** — display credit, dedication, own/family/adapted source and permission details.
7. **Exact World Table preview** — render the same card/page treatment the visitor will eventually see.
8. **Submit for review** — create a private receipt and clearly state that the recipe is not public yet.

## Authority boundary
The browser may prepare and validate a submission, but it cannot grant approval.

Only the moderation backend can transform a reviewed submission into `world-table-contribution/2`.
Only approved records are committed to this repository.

## Suggested private state transition
`DRAFT → SUBMITTED → REVIEW → APPROVED/REJECTED → COMMITTED → PUBLISHED`

The private submission can evolve without changing the public Git record schema.
