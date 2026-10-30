# WF-004 / CHG-012 — Extend R07 to five fine-tuning epochs

User requests five epochs and an explanation of R07 selection. The previous three epochs were a planned compute budget, not an early-stopping result or proof of convergence. R02 was selected among six transfer runs using validation accuracy; R07 started at its best checkpoint. R07 epoch3 then had the highest validation accuracy among the seven original runs.

Continue exactly two epochs from the original R07 last.pt (epoch3), preserving model, Adam state, RNG and DataLoader generator. Same XPU, LR1e-5, batch8, transforms and trainable parameters. New run directory outputs/experiments/R07_5epochs; preserve original R07, original source/config, selection and test artifacts. Explicit checkpoint import lineage and new fingerprint record the extension; do not misrepresent it as a fresh five-epoch run.

Choose best within the five fine-tuning epochs using original validation accuracy/loss/epoch tie-breaking. Also report minimum-validation-loss epoch separately, and inspect overfitting. Five fine-tuning epochs plus the parent training budget is not the same total training budget as five transfer epochs. This follow-up occurs after original test results were viewed, so it is exploratory; do not rerun test or relabel old test results as evaluation of a new checkpoint.

Verification: source/input identity matches original, original checkpoint checksums, exact first-three histories, restored states via existing resume implementation; five history rows, finite metrics, sample counts, checkpoint hashes and TensorBoard steps1–5. Add five-epoch plots and explanation to current notebooks/lab2.ipynb while preserving user edits and historical results. Backup, LOG015 and State update.
