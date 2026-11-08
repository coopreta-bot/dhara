# Data governance

Status: OPEN. This is an engineering rule for the pipeline. It is not a filed DPDP policy. Counsel and the GRC pod must review it before any real corpus is ingested. Mark that review HUMAN REVIEW REQUIRED.

## Rules

- Training and inference data stays inside the same VPC or account boundary as the rest of the platform.
- Every dataset version (DVC or lakeFS) carries a consent and retention record before a training job can read it.
- The local RAG staging pipeline requires consent, retention, provenance, and
  tenant metadata before it writes cleaned chunks. It redacts Aadhaar values,
  labelled account numbers, Indian phone numbers, and email addresses in
  text and citation titles; this is a local gate, not evidence of DPDP/GRC
  approval.
- Farmer Aadhaar fragments, account numbers, and phone numbers are scrubbed or tokenized in the pipeline. A later manual check does not replace that gate.
- Anuppur/Kotma vernacular has its own annotation guideline and a held-out eval split that never enters training.
- RAG indices are partitioned by Party/Organization id.
- Public scheme text, satellite imagery, and mandi bulletins are still tracked with source, retrieval date, and license or access terms.

## Corpora

| Corpus | Source | Used for | Status |
| --- | --- | --- | --- |
| PACS/KCC/UniTERP | Coopreta digitization | SFT and loan-doc skill | OPEN |
| AEPS/DMT/BBPS/CSP | Coopreta CSP operations | Fintech skill, fraud and BI signals | OPEN |
| Legal escalation | RTI and authority letters already in Coopreta's files | Grievance drafts | OPEN |
| Vermicompost SOPs and subsidy filings | NABARD/RKVY/NMSA and internal plans | Ops skill | OPEN |
| Khet Se Baat archive | Coopreta social scripts | Content skill and tone | OPEN |
| Government schemes | Public DPIIT/NABARD/RBI documents | RAG | OPEN |
| Dr. Bacto's and Kalmegh specs | Coopreta product and procurement files | Krishi Salah | OPEN |

No row is cleared for training until its consent record exists. Counsel and GRC
review of the policy remains HUMAN REVIEW REQUIRED before a real corpus is
ingested.
