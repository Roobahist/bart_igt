# Recoverable session results

## Context

The original application accumulated pandas rows and wrote Excel only at shutdown.
It depended on the removed `DataFrame.append` API, used participant codes in paths,
and could lose the whole session on a crash or cleanup failure.

## Decision

Keep the original workbook schema and metadata-first layout. Append completed
responses to a flushed JSONL journal and export via openpyxl to a temporary file
followed by atomic replacement. Use timestamp/UUID filenames and retain journals
for explicit recovery. Keep presentation and task rules separate from persistence.

## Alternatives

Updating pandas concatenation would fix compatibility but retain the crash-loss
risk and add an unnecessary direct dependency for simple tabular export. Saving
an entire workbook after every response would put more work in timed task loops.
A database/service would require disproportionate setup and operational support.

## Consequences

There are two local files to retain and protect. Workbook filenames change, while
columns and row layout remain compatible. Journal writes occur after completed
responses; latency depends on local storage. Recovery exports completed records
but cannot resume a study or restore an interrupted trial. Atomic replacement is
not a guarantee against every filesystem or power-loss failure.
