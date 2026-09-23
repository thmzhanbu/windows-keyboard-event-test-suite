# Evidence, screenshot selection, and remaining work

The strongest result is a documented Windows lab run with **36 passing simulated tests** and successful environment checks. A restored VM export now preserves the source, full report, environment, and verified checksums alongside the screenshots. These establish the recorded test result, not successful live keyboard capture or validation of every later revision.

## What the evidence establishes

| Evidence | What it supports | What it does not establish |
|---|---|---|
| [Full-suite result](screenshots/11-full-test-suite-36-passed.png) | The Windows lab run finished with `36 passed in 0.29s`. | Exact source revision, complete environment header, or real keyboard hooks. |
| [Saved-report verification](screenshots/12-test-report-saved.png) | The report contained `36 passed in 0.25s` at line 44 and `All checks passed` at line 53. Preflight output shows Python 3.14.7, pytest 9.1.1, and pynput 1.8.2. | Access to the complete original Windows text report or validation of operating-system events. |
| [Keyboard-event test details](screenshots/08-keyboard-event-tests-passed.png) | `win32`, Python 3.14.7, pytest 9.1.1, 21 named event tests, and a passing result. | A production keyboard-capture session. These tests use simulated events and mock listeners. |
| [Initial GitHub Actions run](https://github.com/thmzhanbu/windows-keyboard-event-test-suite/actions/runs/35823412189) | Windows and Linux jobs succeeded for maintained-source commit `032e860d84c8c926840812e1a6b9c52a0e79054e`; the Windows job collected 36 tests. | Live keyboard capture, the original VM source, or the status of later commits. |
| [Restored Windows VM export](../reports/restored-windows-vm.md) | Seven Python files, a full report with 36 passes, environment details, and nine verified file hashes; ZIP hash matches screenshot 15. | Original historical report recovery, exact timing, or byte identity with maintained source. |

The different timings in screenshots 11 and 12 are from separate executions. They are observations, not performance benchmarks.

## Source and report provenance

The root source and tests are the maintained project. The [unchanged evidence ZIP](../reports/windows-vm-evidence-bundle.zip) separately preserves the restored Windows VM snapshot. Its fresh report records `win32`, Python 3.14.7, pytest 9.1.1, 36 passing cases, and successful diagnostics. All nine manifest hashes were verified after transfer, and the archive hash matches the Windows screenshot.

The [file comparison](../reports/restored-windows-vm.md#comparison-with-the-maintained-source) documents the differences: comments and formatting, diagnostic wording, a repeated-close simplification, and expanded Unicode samples. Both suites collect 36 cases; the core keyboard-event logic is unchanged. CI tied to a commit validates the maintained revision.

The restored report is a new execution, not the original `test_report.txt` pictured in screenshot 12. Readable UTF-8 report copies are provided, while original bytes remain in the ZIP. The snapshot lacked `requirements.txt` and `pyproject.toml`; the maintained repository provides them. Guest timestamps are preserved with the clock and format caveats documented in the [export notes](../reports/restored-windows-vm.md#time-and-scope-limits).

## Screenshot review

Of the original Windows collection, **08, 11, and 12** are retained. The README features **11 and 13**, with the restored export screenshots **14 and 15** linked as supporting evidence. A separately supplied macOS prototype warning image is described below. Keep the full setup collection as personal lab notes.

| Original filename | Selection | Reason |
|---|---|---|
| `01-python-and-pip-versions.png` | Optional archive | Confirms Python 3.14.7 and pip 26.2.1; mostly blank space and repeated environment information. |
| `02-virtual-environment-created.png` | Optional archive | Shows project creation, virtual-environment creation, and its Python version. Useful setup history. |
| `03-dependencies-installed.png` | Optional archive | Shows successful package installation and versions; screenshot 12 repeats the important versions. |
| `04-project-folder-structure.png` | Omit from showcase | The virtual-environment listing dominates; root files are outside the visible area. The README tree is clearer. |
| `05-log-handler-verification.png` | Redundant | Shows a successful `hello` write/read check; automated tests provide stronger evidence. |
| `06-key-event-simulation.png` | Optional walkthrough | Shows a simulated `a` reaching the buffer and file. Helpful explanation, but much of the image is an unrelated folder listing. |
| `07-log-handler-tests-passed.png` | Optional archive | Shows all 10 log-handler tests passing; the combined result already includes these tests. |
| `08-keyboard-event-tests-passed.png` | **Supporting evidence** | Shows the environment and all 21 named event cases, including lifecycle and failure checks. |
| `09-diagnostics-passed.png` | Redundant | Shows successful preflight checks, which also appear in screenshot 12. |
| `10-diagnostic-tests-passed.png` | Optional archive | Shows five diagnostic tests passing; useful detail already included in the combined result. |
| `11-full-test-suite-36-passed.png` | **Feature** | Clearly shows the complete suite's final result and many test names. |
| `12-test-report-saved.png` | Historical supporting evidence | Connects the earlier test results, diagnostics, and saved report. Screenshot 13 is now featured in the README. |
| `13-windows-vm-report-verified.png` | **Feature** | Connects the restored report to zero exit codes, success markers, and its SHA-256 hash. |
| `14-windows-vm-environment.png` | Supporting evidence | Shows OS and dependency recording. The full text is easier to inspect in reports. |
| `15-windows-evidence-bundle-verified.png` | Supporting evidence | Shows ZIP size, ten files, nine manifest entries, and the archive hash. |

No credentials or personal captured input were visible in the reviewed images. Paths reveal the lab account name `SOC`; screenshot 03 also shows a package maintainer's public email. The terminal text is readable at full size, so images link to their originals. VM clocks vary between early screenshots; do not treat the taskbar dates as a reliable activity timeline.

## Remaining areas and priorities

The separately supplied macOS `Keylogger.py` prototype documents the learning progression. The [project progression](project-evolution.md) preserves it as source text and includes its 4:10 PM permission-warning screenshot as troubleshooting evidence. The raw log is not committed. Its 56 timestamped entries are consistent with the script's format, but they cannot be tied to the pictured launch or used to claim verified Windows integration. The later screenshot repeats the warning and adds a stop message; it is not needed in the showcase.

1. **Restored Windows export completed.** The source, full report, environment, and checksum manifest are preserved and reviewed. Original historical report recovery remains unavailable, but it is not required to demonstrate this clearly labeled restored run.
2. **Initial CI verification completed.** The linked run succeeded on Windows and Linux for commit `032e860d84c8c926840812e1a6b9c52a0e79054e`. The included [CI workflow](../.github/workflows/tests.yml) checks subsequent revisions too; inspect the run for the specific commit being discussed. Historical VM screenshots retain their original meaning.
3. **Keep the integration boundary explicit.** `diagnose.py --live` checks Windows and package availability without opening an input hook. Real Windows event handling remains unverified. Live integration is optional for this project's current testing scope.
4. **Develop failure-path coverage when extending the project.** Useful cases include source-import failures, missing live dependencies, direct write errors, and simultaneous startup/cleanup failures. Add tests for behavior, not merely to increase the count.

The implementation is a small lab project. Its memory buffer grows until cleared, and logs have no rotation, timestamps, or structured event records. Locks protect operations within one handler instance. Lifecycle calls must be serialized by the caller. A periodic flush error is reported during shutdown; it does not automatically stop the listener. If cleanup also fails during startup, its exception can become the top-level error. These constraints should be understood before describing the code as suitable for a long-running service.

## Are more screenshots needed?

No additional screenshot is required for the current evidence package. Screenshots 11 and 13 provide the clearest result; 08, 12, 14, and 15 provide supporting detail. A CI or repository-overview screenshot is optional because the actual pages can be linked. If the source changes and is revalidated in the VM, capture that new result with the environment, command, and summary visible.

For a VM recovery point, save a new snapshot after the export is safely copied outside the VM, using a name such as `keyboard-lab-36-tests-evidence-exported`. Preserve the earlier working snapshot. A VM snapshot helps restore the lab; the exported files and GitHub repository preserve the portfolio artifacts separately. Snapshot creation has not been verified here.
