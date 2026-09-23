# Restored Windows VM: export and verification

The VM snapshot was restored, the full simulated suite and diagnostics were rerun, and the source and evidence were exported together. The [Windows report](windows-vm-verification-report.txt) records **36 passed in 0.26s**, followed by **All checks passed**. Screenshot [13](../docs/screenshots/13-windows-vm-report-verified.png) shows both process exit codes as zero.

## What was preserved

The [original ZIP](windows-vm-evidence-bundle.zip) is 8,207 bytes and contains ten files:

```text
diagnose.py
src/__init__.py
src/keylogger.py
src/log_handler.py
tests/test_diagnose.py
tests/test_keylogger.py
tests/test_log_handler.py
reports/windows-vm-enviroment.txt
reports/windows-vm-verification-report.txt
SHA256SUMS.txt
```

The environment filename is spelled `enviroment` in the original archive. It is preserved exactly. The archive contains no virtual environment, caches, or captured input logs. `requirements.txt` and `pyproject.toml` were absent from the restored snapshot; they were not added to its historical export. The maintained repository provides those setup files.

## Integrity verification

The ZIP checksum matched the one displayed inside Windows, and all nine entries in its manifest matched their archived files after transfer to the Mac. The manifest excludes itself. Screenshots [14](../docs/screenshots/14-windows-vm-environment.png) and [15](../docs/screenshots/15-windows-evidence-bundle-verified.png) show the environment record and bundle inventory.

| Artifact | SHA-256 of original bytes |
|---|---|
| ZIP | `A06D36F2E89F2059FE836FC6B252760AFC23EAFEBED023C665684E8C02451AFA` |
| Windows test report inside ZIP | `A7EA2CF968D716C74F2F17FE293704E6AAFD0F52C8E3B90E231FF070DCC34499` |

A matching hash checks that the transferred bytes match the recorded artifact. It does not independently prove when tests ran or that source files were unchanged between testing and export.

For convenient reading on GitHub, the Windows test report was decoded from UTF-16 to UTF-8 and CRLF line endings were converted to LF. The environment and manifest also have UTF-8/LF copies; only the readable environment copy's filename was corrected. Its recorded text, including the original heading spelling, is unchanged. Verify the original archive members against the manifest, not the converted copies.

## Comparison with the maintained source

All seven Python files were reviewed. Both versions have 36 collected cases: 21 event-handling, 10 log-handler, and 5 diagnostic cases. The core event processing and listener lifecycle follow the same logic. The maintained files are not byte-identical to the VM export.

| File or area | Difference in maintained version | Effect |
|---|---|---|
| `src/keylogger.py` | More explanatory comments and docstrings; formatting changes | Event handling, injected listener, flush worker, and shutdown logic are unchanged. |
| `src/log_handler.py` | `close()` calls the file's close method directly instead of first checking `closed` | Repeated close remains supported for the standard file object used here. |
| `src/__init__.py` | Adds a package docstring to the empty VM file | Documentation only. |
| `diagnose.py` | Clearer missing-package instructions, help text, and failure wording; simpler local expressions | Same preflight checks, no real listener started. |
| `tests/test_keylogger.py` | Uses `hello🙂` instead of `hello!`; adds a timeout assertion message; simplifies local variables | Adds an emoji sample without changing the case count. The VM result does not establish that emoji event case. |
| `tests/test_log_handler.py` | Adds an emoji to the existing `café 日本語` sample | Both exercise Unicode; the maintained sample covers an additional character. |
| `tests/test_diagnose.py` | Expects `pip install` instead of the broader `install` substring | Checks the maintained diagnostic wording more precisely. |

The ZIP is the preserved snapshot. The root `src/`, `tests/`, and `diagnose.py` remain the maintained implementation. Hosted CI validates the maintained implementation for its associated commit.

## Repeating the evidence steps

From the Windows project directory, run each line separately:

```powershell
$pythonPath = ".\.venv\Scripts\python.exe"
& $pythonPath -m pytest tests/ -v --tb=short 2>&1 | Tee-Object -FilePath .\windows-vm-verification-report.txt
$testExitCode = $LASTEXITCODE
& $pythonPath .\diagnose.py --live 2>&1 | Tee-Object -FilePath .\windows-vm-verification-report.txt -Append
$diagnosticExitCode = $LASTEXITCODE
Write-Host "pytest exit code: $testExitCode"
Write-Host "diagnostic exit code: $diagnosticExitCode"
if (($testExitCode -ne 0) -or ($diagnosticExitCode -ne 0)) { throw "Verification failed; inspect the report." }
Select-String -Path .\windows-vm-verification-report.txt -Pattern "36 passed|All checks passed"
Get-FileHash .\windows-vm-verification-report.txt -Algorithm SHA256
```

`Tee-Object` displays and saves the output. Saving each exit code immediately distinguishes an actual successful run from a successful file-writing operation. `Select-String` makes the two result markers easy to locate; the full report preserves the named tests. `Get-FileHash` records the file's checksum before transfer. A rerun will normally produce a different hash because its timings and other output can change.

## Time and scope limits

The archive was supplied and verified on the Mac after export. Guest timestamps are retained as supplied and should not be used to infer exact chronology. The restored VM clock differs from the host, and the environment timestamp command used `HH:ss` (hour and seconds) rather than `HH:mm` (hour and minutes). No timestamp was silently corrected.

This is a fresh verification of the restored snapshot, not the original historical `test_report.txt`. Tests use simulated events and mock listeners. `diagnose.py --live` checks platform and installed distribution metadata; it does not exercise the real Windows input hook. Live capture remains outside the demonstrated result.
