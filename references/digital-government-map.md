# Digital Government Map

This map separates a channel's public purpose from its protected actions. Source
IDs point to the bundled evidence registry; channel profiles add actor, access,
authentication, stop-before, and live-verification metadata. They do not grant
permission to enter a protected service.

## Identity and signature

`profil-zaufany` describes Trusted Profile as an electronic identity and signing
method. It is not an inbox or a general filing portal. The plugin may explain
public prerequisites and hand off its official landing page, then it must stop.
It does not authenticate, create or manage a profile, or sign. Availability of
PESEL does not by itself prove that Trusted Profile or every digital service is
available.

## Service aggregation

`mobywatel` aggregates selected documents and public services. Treat it as a user interface, not a universal identity or records API. The plugin must not enter the app or inspect a personal document or service record.

Do not infer that a residence card, status, or right is represented in
mObywatel. Route the underlying residence question to the competent authority
and treat any displayed digital document as a user-only personal record.

## Correspondence

`epuap` is an electronic correspondence and public-service channel; it is not
the same function as Trusted Profile even when Trusted Profile can be used for
authentication or signing. `epuap` and `e-deliveries` are also distinct from
each other. Determine the receiving authority, sender category, and currently
accepted channel before preparing a generic placeholder draft. The plugin does
not authenticate, address or send correspondence, inspect an inbox, download a
receipt, or preserve personal correspondence.

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
guidance, but it must not create an account, log in through login.gov.pl, enter
an email address or other data, save a draft, attach a file, sign, send, inspect
an acknowledgement, or control the later appointment.

## Work services

Use `praca-gov-pl` for the public service map of the Polish employment portal.
For employer-side permits, declarations, or notifications, identify the
responsible employer or other entrusting entity before describing the route.
Do not present praca.gov.pl as a worker-controlled universal filing channel or
infer that an employer action completes the worker's stay route. Filing and
authenticated employer records remain outside the plugin boundary.

## Personal systems

- immigration: `mos-residence`;
- tax: `e-tax-office`;
- social insurance: `ezus`;
- health: `ikp`;
- business: `biznes-ceidg`;
- family and social services: `empatia`.

Each system has public guidance and authenticated effects. Use only its public guidance and exact official landing page. Login, authenticated reads, personal-record access, submissions, uploads, downloads, signatures, payments, and mutations are prohibited even with user consent.

In particular, e-Tax Office (`e-tax-office`) and eZUS (`ezus`) are protected
personal systems after authentication. Public tax or social-insurance guidance
may be researched separately, but the plugin never reads a return, balance,
certificate, contribution record, insured-person record, message, or case state.

## Municipal identity records

Use `gov-pesel-foreigners`, `gov-meldunek-foreigners`, and `gov-civil-record-copy` for preparation. The competent gmina owns the local action. Collect locality and document context before routing.

## Transition risk

Digital-service names, login options, delivery channels, and click paths change faster than the underlying authority map. Recheck only public official pages within their freshness window and phrase navigation semantically. Stop at the first protected or interactive boundary.
