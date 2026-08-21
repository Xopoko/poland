# Documents and Language

## Document routing

Identify four facts before recommending document work:

1. document type and issuing authority;
2. issuing country and original language;
3. receiving authority and intended procedure;
4. target date and whether the receiving authority published current requirements.

Use `gov-civil-record-copy` for Polish civil-record copies, `sworn-translators` to locate the official translator register, `apostille` for legalization routing, and `nawa-recognition` for foreign education recognition.

Do not order translation, apostille, legalization, or recognition based on a generic checklist. The receiving authority determines what it will accept.

## Language labels

The `languages` field in `data/sources.json` means that the authority exposes relevant material or a service path in that language. It does not guarantee complete translation, current parity, or service by an officer in that language.

Prefer a current Polish procedure page over an older translation, while explaining the language limitation. For material consequences, compare dates and escalate unclear differences.

## Translation quality

Machine translation may support orientation but is not a sworn translation.
Preserve the original official title, source ID, and URL when translating public
guidance. Keep identity data, personal documents, and legal declarations out of
bundled plugin tools and public-source evidence.

For a user-selected personal document, a caller-owned tool may inspect or produce
an orientation translation only after explicit task-scoped authorization. Show
the limitation clearly, minimize exposed data, do not persist the document in
plugin artifacts, and never present machine output as a sworn translation or
accept a legal declaration for the user.

## Document safety

Use only non-identifying document categories in bundled plugin tools. In a
caller-owned task context, inspect or transform the minimum selected document
only after explicit scope authorization. Upload, download, ordering, payment
initiation, or submission requires a fresh summary of the exact document,
official origin, destination, purpose, fee, and action-time confirmation.
Signatures, attestations, final payment authorization, irreversible surrender of
an original, and certification of authenticity or legal sufficiency remain with
the user or qualified professional.
