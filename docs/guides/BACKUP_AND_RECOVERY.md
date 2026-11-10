# Backup and recovery plan

**Status:** Design only; no database or production data is configured.

## Data to protect

- Approved source metadata, document versions and hashes, evidence locators, reviewed claim/rule records, review events, and evaluation materials.
- Do not back up API keys into database snapshots or repository archives.
- Do not collect citizen profiles, uploaded documents, or chat history in the initial product.

## Proposed controls before production

1. Use automated encrypted database backups with documented retention and region.
2. Export reviewed content metadata and migration versions to a protected repository or approved storage with least-privilege access.
3. Keep canonical official source links and permitted minimal excerpts; do not assume source documents may be redistributed.
4. Monitor backup completion and age; alert on missed jobs without logging private records.
5. Test restoration into an isolated non-production database before launch and on a schedule.
6. Record restore duration and data-loss window and compare them with pilot requirements.

## Recovery sequence

1. Stop writes and identify the last known-good backup/schema version.
2. Restore to an isolated database and run integrity checks on source relationships, evidence references, review status, and migration history.
3. Verify a sample of published claims and source URLs against the human-reviewed registry.
4. Re-enable service only after a reviewer confirms currentness and operations verifies secrets/permissions.
5. Document the recovery event and any content requiring re-review.

No backup job, restore, or production data operation has been performed.
