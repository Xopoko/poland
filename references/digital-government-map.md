# Digital Government Map

This map separates a channel's public purpose from its protected actions. Source
IDs point to the bundled evidence registry; channel profiles add actor, access,
authentication, stop-before, and live-verification metadata. They do not grant
permission by themselves. For an installed caller-owned tool, apply the task
scope, authentication handoff, action-time confirmation, and user-only controls
in `automation-playbook.md`. A channel `stop_before` entry means pause and
classify that effect, not assume blanket prohibition.

## Identity and signature

`profil-zaufany` describes Trusted Profile as an electronic identity and signing
method. It is not an inbox or a general filing portal. The plugin may explain
public prerequisites and open its official landing page. The user chooses the
identity provider, enters secrets, completes 2FA, and applies every signature or
legal attestation. After the user reports authentication complete, an installed
caller-owned tool may resume the separately authorized administrative task, but
it must not observe the authentication step. Availability of PESEL does not by
itself prove that Trusted Profile or every digital service is available.

## Service aggregation

`mobywatel-web` and `mobywatel-mobile` expose overlapping documents and public
services through separate browser and smartphone surfaces. Treat neither as a
universal identity or records API. Personal documents and service records may
be inspected only to the minimum extent needed for the explicitly authorized
task in a caller-owned tool; they never become public source evidence or plugin
data. Mobile activation, biometrics, document presentation, and app-local
secrets remain user-controlled.

Do not infer that a residence card, status, or right is represented in
mObywatel. Route the underlying residence question to the competent authority
and treat any displayed digital document as private, task-scoped case evidence.

## Correspondence

`epuap` is an electronic correspondence and public-service channel; it is not
the same function as Trusted Profile even when Trusted Profile can be used for
authentication or signing. `epuap` and `e-deliveries` are also distinct from
each other. Determine the receiving authority, sender category, and currently
accepted channel before preparing a generic placeholder draft. The plugin does
not authenticate or preserve personal correspondence. After user-only
authentication and explicit scope authorization, a caller-owned tool may inspect
the relevant inbox item, address and prepare a message, or locate a receipt.
Sending, uploading, and downloading require a fresh action-time confirmation;
signing remains user-controlled.

## Residence through MOS

Use `udsc-mos-electronic-residence` for the current electronic-channel rule and
`mos-residence` for the MOS landing page. The Office for Foreigners guidance
states that from 27 April 2026 temporary, permanent, and long-term EU resident
permit applications are generally lodged electronically through MOS, while it
lists specific temporary-residence cases that remain on the paper route. Verify
the exact purpose-of-stay branch and transition date at action time; do not turn
the general rule into a universal claim.

An ordinary MOS route separates several actors: the foreigner controls the
application and signature; an employer, university, traineeship organiser, or
voluntary-work organiser may control a required electronic attachment; and the
voivode later controls an in-person request for fingerprints, specimen
signature, original passport presentation, or supplementation. These are all
user- or third-party-owned actions. The plugin may describe them from public
guidance. In caller-owned operator mode, the user authenticates and authorizes
the exact actor and task; the agent may then inspect the relevant state and fill
necessary fields. Account creation, server-side draft creation, attachment,
submission, download, and appointment changes require their own visible summary
and action-time confirmation. The user applies the signature, attests to truth,
and completes in-person steps. Never operate an employer or institution account
under authority granted only by the foreigner.

## Work services

Use `praca-gov-pl` for the public service map of the Polish employment portal.
For employer-side permits, declarations, or notifications, identify the
responsible employer or other entrusting entity before describing the route.
Do not present praca.gov.pl as a worker-controlled universal filing channel or
infer that an employer action completes the worker's stay route. Filing and
authenticated employer records require authorization from that account's actor,
not merely from the foreign worker. The agent may assist that authorized actor
under the shared operator contract; signatures and legal attestations remain
with the actor.

## Personal systems

- immigration: `mos-residence`;
- tax: `e-tax-office`;
- social insurance: `ezus`;
- health: `ikp`;
- business: `biznes-ceidg`;
- family and social services: `empatia`.

Each system has public guidance and authenticated effects. Research the public
guidance first, identify the correct actor and service, and then apply the shared
operator contract if the user requests hands-on help. The user performs login,
secrets, CAPTCHA/2FA, signatures, attestations, and final payment authorization.
Minimum task-relevant reads and form filling need explicit scope authorization;
submissions, sends, bookings, uploads, downloads, payment initiation, and record
changes need fresh action-time confirmation.

In particular, e-Tax Office (`e-tax-office`) and eZUS (`ezus`) are protected
personal systems after authentication. Public tax or social-insurance guidance
must be researched separately. A caller-owned tool may read a return, balance,
certificate, contribution record, insured-person record, message, or case state
only when that item is necessary for the explicitly authorized task; do not copy
it into a source receipt or bundled plugin tool.

## Municipal identity records

Use `gov-pesel-foreigners`, `gov-meldunek-foreigners`, and
`gov-civil-record-copy` for preparation. The competent gmina owns the local
action. Collect locality and document context before routing. Online form or
booking assistance follows the same user-authentication and action-confirmation
contract.

## Transition risk

Digital-service names, login options, delivery channels, and click paths change
faster than the underlying authority map. Recheck public official pages within
their freshness window and phrase navigation semantically. At protected or
interactive boundaries, pause, verify the state, and apply the appropriate
handoff or confirmation; if the expected control cannot be verified, use guided
manual fallback.
