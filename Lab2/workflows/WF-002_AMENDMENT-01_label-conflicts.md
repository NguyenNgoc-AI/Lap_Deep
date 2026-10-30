# WF-002 amendment 01 — 2026-10-30

Actual audit found 13 byte-identical groups with conflicting labels (26 files: 23 train and 3 test). Evidence: outputs/data/label_conflicts.json. The original fail-fast check worked and stopped the phase before a manifest or training was created.

Under the user's explicit instruction to carry the work to completion, quarantine every TRAIN member of those groups from the derived manifest. Do not relabel images, change test membership, or modify/delete any raw file. Preserve all 3,000 test images and report this label ambiguity as a limitation. Continue ordinary train duplicate/test-overlap filtering and seeded stratified splitting after quarantine. Record reasons and every excluded path in audit.json.

This is an explicit implementation amendment to WF-002 section 6, not a claim that the original data was conflict-free. All other model, epoch, batch and learning-rate settings remain as locked. The default make_split contract still rejects conflicting labels; the actual dataset pipeline opts into this documented quarantine policy.
