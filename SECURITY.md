# Security

## What this repository is

A research proof of concept about confidentiality, not a product. Do not use it to
process real client data.

## Threat model

- **Zero trust in the cloud.** The cloud operator, its staff, co-tenants and anyone with
  physical access are treated as adversaries, and so are chip vendors: no TEE (SEV, TDX,
  GPU confidential computing) is relied on.
- **The one trusted endpoint is the firm's own device** (the lawyer's laptop). It holds the
  client account and runs the device model offline. Securing that endpoint (disk
  encryption, patching, malware) is the firm's responsibility and is out of scope here.
- **The cloud LLM sees only public law.** It is used offline to precompute reasoning over
  public statute text, never with client data, so no trust in it is needed.

## Attack code

`attacks/` contains attacks against the keyed weight-shift scheme in `keyed/`. That scheme
is this project's own candidate design; the attacks exist to evaluate it, and they show it
fails. They target nothing else.

## Known limitations

These are documented in `REPORT.md`, notably:

- The egress guard (`device/egress.py`) blocks the channels tested; production use would
  need a complete, audited taint-tracking of every code path.
- The PIR parameters are research-grade (SimplePIR over Z_2^32, LWE dimension 512) and have
  not been reviewed for a production security level.
- The final round's pre-registered verdict is FAIL (task routing 7/8).

## Reporting

Please report security issues privately via GitHub's "Report a vulnerability"
(Security tab), or to abdullah@memonsystems.com. Please do not open a public issue for a
vulnerability.
