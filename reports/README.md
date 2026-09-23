# Verification reports

## Restored Windows VM

- [Full test and diagnostic report](windows-vm-verification-report.txt): 36 tests passed in 0.26 seconds, followed by successful preflight checks.
- [Environment record](windows-vm-environment.txt): Windows 11 Pro build 26200, Python and installed package versions.
- [Original evidence ZIP](windows-vm-evidence-bundle.zip): seven Python source/test files, two reports, and their checksum manifest, unchanged from the VM export.
- [File checksum manifest](windows-vm-SHA256SUMS.txt): nine entries; paths refer to files inside the archive.
- [Verification and source comparison](restored-windows-vm.md): hash results, source differences, encoding notes, and evidence limits.

The text files above are readable UTF-8 copies with LF line endings. The original bytes and filenames remain in the ZIP. The manifest hashes apply to the archived originals, not these converted copies.

## Maintained source on macOS

`macos-verification.txt` records 36 passing tests and successful diagnostics for the maintained source on macOS. `macos-environment.txt` records the installed packages for that run.

The earlier Windows lab results and the restored VM export are shown in [the selected screenshots](../docs/screenshots/README.md). The restored report is a new verification run, not a recovery of the earlier `test_report.txt` pictured in screenshot 12.

For the published revision, also inspect its actual GitHub Actions result.
