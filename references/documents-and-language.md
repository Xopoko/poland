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

Machine translation may support orientation but is not a sworn translation. Preserve the original official title, source ID, and URL when translating public guidance. Do not inspect or translate identity data, personal documents, or legal declarations; user review does not expand this boundary.

## Document safety

Do not request, inspect, store, translate, transmit, upload, or download passports, residence cards, civil records, health documents, financial statements, or attachments. Route only from non-identifying document categories. The plugin may hand off the exact official landing page and then stop.
