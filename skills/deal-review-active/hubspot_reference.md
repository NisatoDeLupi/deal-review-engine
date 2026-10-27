# HubSpot Reference — Xoxoday/Giift Account

Reference IDs, stage mappings, and API quirks specific to the Xoxoday HubSpot setup. Update these if anything changes.

## Account
- Account ID: `1234567`
- URL pattern for deal links: `https://app.hubspot.com/contacts/1234567/record/0-3/<deal_id>`

## Owner IDs

| Person | Role | Owner ID |
|---|---|---|
| Abhimanyu Shekhawat | Manager (RevOps/Sales Leadership) | `900000011` |
| AE_13 | AE | `900000113` |
| AE_27 | AE | `900000115` |
| SDR_Q | AE | `900000080` |
| AE_74 | AE | `900000015` |

If new AEs join the hunting team, add them here. Always verify with `HubSpot:search_owners` if uncertain — IDs occasionally change after re-provisioning.

## Pipeline stages

Stages span multiple product pipelines (Empuls, Compass, Plum, Loyalife/LBMS). Use the dealstage label rather than ID when possible, since IDs differ across pipelines.

Active stages (include in review):
- `1 - Prospect`
- `2 - Need Analysis & Solutioning`
- `3 - Opportunity`
- `4 - Proposal`
- `5 - Negotiation`

Closed stage IDs to EXCLUDE:
- Closed-won: `9000000002`, `900000074`, `900000075`, `9000000013`, `900000076`
- Closed-lost: `closedlost`, `90000039`, `9000000011`, `900000055`

## Product / pipeline mapping

| Product | ACV treatment |
|---|---|
| Empuls | 100% of deal amount |
| Compass | 100% of deal amount |
| Plum | 3% of GMV counts as ACV (apply haircut when reporting team ACV) |
| Loyalife / LBMS | 100% of deal amount |

When showing pipeline value to leadership, apply the Plum haircut. When showing deal-level numbers for AE coaching, leave amounts as recorded.

## API quirks and limits

- **`manage_crm_objects` batch size**: hard cap of 10 objects per call. Trying 11+ fails the entire batch with `VALIDATION_ERROR`.
- **No delete via MCP**: `manage_crm_objects` supports create and update only. Test entries that need removal must be manually archived in HubSpot UI.
- **Mention HTML**: only `<span data-mention-id="..." data-mention-name="...">` triggers notifications. Plain text mentions render but don't notify.
- **Currency formatting**: `amount` is in `deal_currency_code` units. Always check `deal_currency_code` before INR conversion.
- **Multi-currency conversion** (approximate, update quarterly):
  - USD → INR: 90
  - AED → INR: 25
  - SGD → INR: 68
  - EUR → INR: 96
  - GBP → INR: 113

## Common search filters

To pull all open hunting team deals:
```json
{
  "objectType": "deals",
  "filters": [
    {
      "propertyName": "hubspot_owner_id",
      "operator": "IN",
      "values": ["900000113", "900000115", "900000080", "900000015"]
    },
    {
      "propertyName": "dealstage",
      "operator": "NOT_IN",
      "values": ["9000000002", "900000074", "900000075", "9000000013", "900000076", "closedlost", "90000039", "9000000011", "900000055"]
    }
  ],
  "properties": ["dealname", "dealstage", "amount", "deal_currency_code", "hubspot_owner_id", "closedate", "createdate", "hs_lastmodifieddate", "pipeline"]
}
```

## Engagement retrieval (notes, emails, calls)

Two-step process for each deal:

### Step 1: Get associated engagement IDs

```json
{
  "objectType": "deals",
  "objectIds": ["<deal_id>"],
  "associations": ["notes", "emails", "calls"]
}
```

This returns an `associations` block with IDs grouped by type. Collect all three lists.

### Step 2: Fetch engagement bodies in batches

For each engagement type, call `HubSpot:get_crm_objects` with the relevant `objectType` and properties.

**Notes:**
```json
{
  "objectType": "notes",
  "objectIds": ["<note_id_1>", "<note_id_2>"],
  "properties": ["hs_note_body", "hs_timestamp", "hubspot_owner_id"]
}
```
Body field: `hs_note_body` (HTML — strip tags for reading)

**Emails:**
```json
{
  "objectType": "emails",
  "objectIds": ["<email_id_1>", "<email_id_2>"],
  "properties": ["hs_email_subject", "hs_email_text", "hs_email_html", "hs_email_direction", "hs_email_status", "hs_email_from_email", "hs_email_to_email", "hs_timestamp", "hubspot_owner_id"]
}
```
Body field: prefer `hs_email_text` (plain text). Fall back to `hs_email_html` (strip tags). Use `hs_email_direction` to classify INCOMING vs OUTGOING. `hs_email_status` indicates SENT/BOUNCED/etc.

**Calls:**
```json
{
  "objectType": "calls",
  "objectIds": ["<call_id_1>", "<call_id_2>"],
  "properties": ["hs_call_title", "hs_call_body", "hs_call_duration", "hs_call_direction", "hs_call_disposition", "hs_call_status", "hs_call_recording_url", "hs_timestamp", "hubspot_owner_id"]
}
```
Body field: `hs_call_body` (rep-typed call notes — usually the most valuable content). `hs_call_disposition` indicates outcome (CONNECTED / NO_ANSWER / LEFT_VOICEMAIL / BUSY / WRONG_NUMBER). `hs_call_duration` is in milliseconds. If `hs_call_recording_url` exists, surface it but don't try to play audio.

### Batch limits

`get_crm_objects` accepts up to ~100 IDs per call. For deals with very long engagement histories (50+ emails over 2 years), paginate or sample the most recent 30 entries — older context is less actionable.

### Direction values reference

| Field | Value | Meaning |
|---|---|---|
| `hs_email_direction` | `EMAIL` | Outbound email sent by rep |
| `hs_email_direction` | `INCOMING_EMAIL` | Inbound email from customer |
| `hs_email_direction` | `FORWARDED_EMAIL` | Forwarded thread |
| `hs_call_direction` | `OUTBOUND` | Rep called customer |
| `hs_call_direction` | `INBOUND` | Customer called rep |

### Disposition values reference (calls)

| Value | Meaning |
|---|---|
| `CONNECTED` | Call answered, conversation happened |
| `NO_ANSWER` | Customer didn't pick up |
| `LEFT_VOICEMAIL` | Voicemail left |
| `BUSY` | Line busy |
| `WRONG_NUMBER` | Wrong contact details |
| `LEFT_LIVE_MESSAGE` | Spoke to gatekeeper/colleague |

When reporting call activity, only `CONNECTED` and `LEFT_LIVE_MESSAGE` count as "real attempts" — others are just dial attempts.
