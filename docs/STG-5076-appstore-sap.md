# STG-5076: App Store SAP authentication

## Problem and acceptance

Fresh App Store authentication currently exhausts unsigned endpoint retries. A real
CLI run from main 28c0b18 failed after 17 POSTs and 769 seconds. PyPI 2026.8.6 also
fails and predates PR #149. Upstream ipatool v2.5.0 uses SAP-signed authentication.

Implement locally first. Publishing a PR, merging and releasing are conditional on
successful cold authentication and a valid IPA through the actual CLI entry point.
A second process must download using its saved session. Then integrate the proven
implementation into Markea and the monolith, test on dev and finish STG-5071 pod
replacement acceptance. Do not automatically promote staging or production.

## Design

- Retain Python StoreClient and download/session interfaces.
- Fetch Apple's bag over verified TLS and validate its authentication and SAP URLs.
- Use a small subprocess adapter around the unmodified SAP signer from pinned
  ipatool v2.5.0 (d5d0b56faf64e3fdef885d49e7928b390aadb6c7).
- Build the adapter inside a verified temporary upstream source tree. Bundle
  compiled helpers for Linux and macOS on amd64/arm64 in release artifacts, with
  Windows support where build checks permit. No Go toolchain is required at runtime.
  Keep the adapter source and reproducible build instructions in this repository.
- The helper receives configuration and exact request bytes as bounded JSON lines
  through stdin, returns signatures through stdout and never logs payloads. No
  account credentials in process arguments. Initialize once per login, sign each
  POST, close in finally. Enforce setup and sign deadlines and reap failed helpers.
- Use X-Apple-ActionSignature (base64) for the exact serialized plist bytes. GUID
  is the hex encoding of the hardware bytes passed to the signer.
- Use only the bag authentication endpoint; validate every redirect before
  forwarding credentials. Preserve body/attempt across pod redirects and transient
  response retries. Limit redirects, protocol retries and HTTP retries explicitly.
- No unsigned fallback. Classify missing/invalid SAP configuration, signature
  failures, temporary Apple responses and authentication failures separately.
- Upstream downloads its pinned, checksum-verified Unicorn runtime and Apple
  framework assets on the first use. Document/cache these separately from account
  sessions. Do not redistribute Apple frameworks in our package.

## Checks

- Unit coverage: exact signed bytes, bag validation, malicious redirects, malformed
  and oversized helper responses, timeout/crash cleanup, 2FA/provider failures,
  bounded retry behavior and unchanged successful download flow.
- Helper build and protocol tests; complete existing CLI test suite.
- Actual cold and warm CLI download with isolated cache and private credentials.
- Verify published wheel and Docker version/content only after local acceptance.
- Preserve Markea JSON session persistence and database locking.

## Sources

- https://tracker.yandex.ru/STG-5076
- https://github.com/majd/ipatool/pull/525
- https://github.com/majd/ipatool/releases/tag/v2.5.0

## Local acceptance, 2026-09-07

- Actual CLI cold login with empty account cache: signed POSTs 302 -> 200,
  valid IPA 113,364,008 bytes, exit 0 in 35.13 seconds including first SAP setup.
- Second CLI process: saved session restored, zero auth POSTs, valid IPA,
  exit 0 in 7.13 seconds.
- Installed wheel 2026.9.1, separate empty account cache: signed POSTs 302 -> 200,
  valid IPA 113,364,009 bytes, exit 0 in 10.16 seconds (runtime assets already cached).
- 241 Python tests pass. All six native targets build from the pinned Go module.
- Linux amd64 Debian helper starts; Alpine amd64 completes real anonymous SAP
  setup and creates a 501-byte signature in 25 seconds. Alpine uses its installed
  musl loader explicitly because purego's default ELF interpreter names glibc.
- Docker base aligned to Python 3.12, already required by the Python package.
  Apple assets remain runtime downloads and are not bundled in released images.
