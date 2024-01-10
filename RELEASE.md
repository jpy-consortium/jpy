# Release

Jpy is built and released across a matrix of operating systems, architectures, and Python versions.

The jar artifacts are Java 8+ compatible and released to [org.jpyconsortium:jpy](https://repo1.maven.org/maven2/org/jpyconsortium/jpy) on Maven Central.

The wheel artifacts are compatible with the table below, and released to the PyPi package [jpy](https://pypi.org/project/jpy/).

| Version | OS      | Arch   |
|---------|---------|--------|
| 3.6     | Linux   | x86_64 |
| 3.7     | Linux   | x86_64 |
| 3.8     | Linux   | x86_64 |
| 3.9     | Linux   | x86_64 |
| 3.10    | Linux   | x86_64 |
| 3.11    | Linux   | x86_64 |
| 3.12    | Linux   | x86_64 |
| 3.6     | Linux   | arm64  |
| 3.7     | Linux   | arm64  |
| 3.8     | Linux   | arm64  |
| 3.9     | Linux   | arm64  |
| 3.10    | Linux   | arm64  |
| 3.11    | Linux   | arm64  |
| 3.12    | Linux   | arm64  |
| 3.6     | MacOS   | x86_64 |
| 3.7     | MacOS   | x86_64 |
| 3.8     | MacOS   | x86_64 |
| 3.9     | MacOS   | x86_64 |
| 3.10    | MacOS   | x86_64 |
| 3.11    | MacOS   | x86_64 |
| 3.12    | MacOS   | x86_64 |
| 3.6     | MacOS   | arm64  |
| 3.7     | MacOS   | arm64  |
| 3.8     | MacOS   | arm64  |
| 3.9     | MacOS   | arm64  |
| 3.10    | MacOS   | arm64  |
| 3.11    | MacOS   | arm64  |
| 3.12    | MacOS   | arm64  |
| 3.6     | Windows | x86_64 |
| 3.7     | Windows | x86_64 |
| 3.8     | Windows | x86_64 |
| 3.9     | Windows | x86_64 |
| 3.10    | Windows | x86_64 |
| 3.11    | Windows | x86_64 |
| 3.12    | Windows | x86_64 |

## Process

The [build.yml](.github/workflows/build.yml) workflow is the main process by which PRs and releases are built.
The release process is kicked off whenever a branch name matches `release/v*` is pushed to [jpy-consortium/jpy](https://github.com/jpy-consortium/jpy).
