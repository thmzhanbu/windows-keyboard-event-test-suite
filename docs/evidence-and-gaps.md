# Evidence, screenshot selection, and remaining work

The strongest result is a documented Windows lab run with **36 passing simulated tests** and successful environment checks. The screenshots support that result. They do not establish successful live keyboard capture or validate every later revision of the code.

## What the evidence establishes

| Evidence | What it supports | What it does not establish |
|---|---|---|
| [Full-suite result](screenshots/11-full-test-suite-36-passed.png) | The Windows lab run finished with `36 passed in 0.29s`. | Exact source revision, complete environment header, or real keyboard hooks. |
| [Saved-report verification](screenshots/12-test-report-saved.png) | The report contained `36 passed in 0.25s` at line 44 and `All checks passed` at line 53. Preflight output shows Python 3.14.7, pytest 9.1.1, and pynput 1.8.2. | Access to the complete original Windows text report or validation of operating-system events. |
| [Keyboard-event test details](screenshots/08-keyboard-event-tests-passed.png) | `win32`, Python 3.14.7, pytest 9.1.1, 21 named event tests, and a passing result. | A production keyboard-capture session. These tests use simulated events and mock listeners. |
| [Initial GitHub Actions run](https://github.com/thmzhanbu/windows-keyboard-event-test-suite/actions/runs/35823412189) | Windows and Linux jobs succeeded for maintained-source commit `032e860d84c8c926840812e1a6b9c52a0e79054e`; the Windows job collected 36 tests. | Live keyboard capture, the original VM source, or the status of later commits. |

The different timings in screenshots 11 and 12 are from separate executions. They are observations, not performance benchmarks.

## Source and report provenance

This repository is a maintained copy of the existing local project. It is **not an exported snapshot of the Windows VM**. The lab walkthrough and screenshots document the user's Windows run, while the locally available project and its earlier text report came from the original macOS build. That earlier report recorded `darwin` and pytest 8.4.2.

There are small differences between the original local files and the code entered during the Windows walkthrough. A matching test count does not prove the files are identical. Treat the Windows screenshots as historical evidence, and use a fresh test report or CI run tied to a commit to validate the maintained source.

The complete Windows `test_report.txt` has not been supplied with the screenshot folder. Screenshot 12 confirms that it existed in the VM; it is not a substitute for the file itself. No replacement Windows report has been fabricated from the images.

## Review of all 12 screenshots

Only **08, 11, and 12** are included in this repository. Keep the original full collection as personal lab notes. A short portfolio should emphasize results and reasoning rather than every setup action.

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
| `12-test-report-saved.png` | **Feature** | Connects test results, diagnostics, and verification of the saved report. |

No credentials or personal captured input were visible in the reviewed images. Paths reveal the lab account name `SOC`; screenshot 03 also shows a package maintainer's public email. The terminal text is readable at full size, so images link to their originals. VM clocks vary between early screenshots; do not treat the taskbar dates as a reliable activity timeline.

## Remaining areas and priorities

1. **Preserve the original Windows report and source.** Export them from the VM if exact historical reproducibility is needed. Keep them separately identified from the maintained version.
2. **Initial CI verification completed.** The linked run succeeded on Windows and Linux for commit `032e860d84c8c926840812e1a6b9c52a0e79054e`. The included [CI workflow](../.github/workflows/tests.yml) checks subsequent revisions too; inspect the run for the specific commit being discussed. Historical VM screenshots retain their original meaning.
3. **Keep the integration boundary explicit.** `diagnose.py --live` checks Windows and package availability without opening an input hook. Real Windows event handling remains unverified. Live integration is optional for this project's current testing scope.
4. **Develop failure-path coverage when extending the project.** Useful cases include source-import failures, missing live dependencies, direct write errors, and simultaneous startup/cleanup failures. Add tests for behavior, not merely to increase the count.

The implementation is a small lab project. Its memory buffer grows until cleared, and logs have no rotation, timestamps, or structured event records. Locks protect operations within one handler instance. Lifecycle calls must be serialized by the caller. A periodic flush error is reported during shutdown; it does not automatically stop the listener. If cleanup also fails during startup, its exception can become the top-level error. These constraints should be understood before describing the code as suitable for a long-running service.

## Are more screenshots needed?

No additional screenshot is needed to document the existing 36-test run. The initial successful CI result is linked above; a screenshot of it or a repository overview is optional. Check the actual CI result for later commits. If the source changes and is revalidated in the Windows VM, capture that new result with the environment, command, and summary visible. Do not retake or edit historical screenshots merely to match a newer test count.
