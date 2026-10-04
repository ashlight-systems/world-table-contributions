# World Table Git V2 compatibility update

Purpose: align the approved Git record with World Table V1.6.1 moderation.

Changes:
- flexible normalized ingredient units such as cup, oz, lb, stick, can, bunch and stalk
- resolved external-source rights values including CC BY-NC-SA 3.0
- optional rights.sourceCreator provenance field
- UNKNOWN remains valid only in private moderation and is rejected from approved Git
- README/contribution guidance now describes mixed per-record rights
- adds a licensed-source example that exercises cup/stick units and CC BY-NC-SA 3.0

Acceptance before packaging:
- tools/test_validate.py: 58 passed, 0 failed
- tools/validate.py: 2 example files checked, 0 with problems

Suggested branch: recipe-schema-v2-rights-units
Suggested commit: Align V2 with flexible units and source licences
