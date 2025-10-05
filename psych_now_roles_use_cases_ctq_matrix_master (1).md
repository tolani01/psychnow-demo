# PsychNow — Role Catalog, Use Case Inventory & CTQ Matrix (Master)

> Scope: Based on the current PsychNow functional spec. This document enumerates **user roles**, **end‑to‑end use cases**, and **critical‑to‑quality (CTQ)** requirements with measurable targets, edge‑cases, and acceptance notes suitable for PRD import.

---

## Table of Contents
1. [Role Catalog & RBAC Overview](#role-catalog--rbac-overview)
2. [Use Case Inventory (by Domain)](#use-case-inventory-by-domain)
3. [CTQ by Role (KPIs & SLAs)](#ctq-by-role-kpis--slas)
4. [Edge‑Case Catalog & Controls](#edge-case-catalog--controls)
5. [RACI for Critical Processes](#raci-for-critical-processes)
6. [Acceptance Criteria Snapshots](#acceptance-criteria-snapshots)
7. [Post‑MVP Backlog & Dependencies](#post-mvp-backlog--dependencies)

---

## Role Catalog & RBAC Overview

### Primary Roles
1. **Patient (Self‑Pay)** — Seeks evaluation/med management and/or therapy.
   - Scope: onboarding/intake, scheduling, telehealth, payments, messaging, documents.
2. **Injury Patient (LOP)** — Similar to Patient but under attorney lien.
   - Scope: LOP intake, care under funding limits, records & status transparency.
3. **Attorney** — Refers, monitors case, obtains reports/invoices for demand/settlement.
   - Scope: referral intake, document vault, case status, messaging, ledger access.
4. **Case Manager (Attorney/Funder)** — Operationally manages multiple LOP cases.
   - Scope: batched updates, status exports, notifications, ledger reconciliations.
5. **Lien Funder Analyst/Underwriter** — Approves cases, sets limits, tracks exposure.
   - Scope: case review, approval/decline, cap adjustments, drawdowns, settlements.
6. **Provider (Prescriber: Psychiatrist/PMHNP)** — Conducts evals/follow‑ups, prescribes.
   - Scope: schedule, visit, eRx/EPCS, PDMP, documentation, messaging, payouts view.
7. **Provider (Therapist/LCSW/PhD)** — Delivers therapy care plans.
   - Scope: schedule, visit, notes, homework, messaging, outcomes tracking.
8. **Scheduler / Care Coordinator (MSO)** — Manages calendars, escalations, patient comms.
   - Scope: triage, booking, reminders, waitlist, exception handling, tasks.
9. **Billing & Finance (MSO)** — Self‑pay collections, refunds, provider payouts; LOP ledgers.
   - Scope: invoices, reconciliation, payout runs, settlement accounting.
10. **Compliance & Privacy Officer** — HIPAA/42 CFR Part 2 oversight, access audits.
    - Scope: audit logs, minimum‑necessary policies, incident response.
11. **Clinical Director / QA** — Quality of care, documentation, protocols.
    - Scope: chart audits, policy engine, corrective actions, training.
12. **Content/Marketing (Non‑PHI)** — Web content, SEO/ads, funnel analytics.
    - Scope: CMS, landing tests, attribution; no PHI access.
13. **Super Admin (Platform Owner)** — Tenancy, integrations, feature flags, IAM.
    - Scope: environment config, partner selection (eRx/telehealth), data retention.

### RBAC Guardrails (summary)
- **Least privilege** by default; **minimum necessary** for PHI.
- **Segregation of duties**: Billing vs Compliance vs Clinical.
- **Partitioned surfaces**: Marketing stack isolated from PHI systems.
- **State‑aware** access**:** licensure, PDMP rules, EPCS.

---

## Use Case Inventory (by Domain)
> Each use case lists *Actors, Trigger, Preconditions, Main Flow, Alt/Exceptions, Data, Notifications & Audit*. IDs are stable for PRD import.

### A) Identity, Accounts & Consent
- **UC‑ID‑01: Patient Sign‑Up (Self‑Pay)**  
  **Actors:** Patient  
  **Trigger:** Start intake/booking  
  **Pre:** unique email/phone; age ≥18 or guardian  
  **Flow:** register → verify (OTP/email) → create profile → accept HIPAA/ToS/telehealth consent  
  **Alt:** minor/guardian flow; duplicate account merge; email taken → account recovery  
  **Data:** demographics, contacts, consents (versioned)  
  **Notify/Audit:** welcome + verification receipts; consent audit trail

- **UC‑ID‑02: Guardian/Proxy Access**  
  **Actors:** Guardian, Patient, Admin  
  **Flow:** invite guardian → identity attestation → proxy scope (read/limited write) → revoke

- **UC‑ID‑03: Provider Onboarding & ID Proofing (EPCS)**  
  **Actors:** Provider, Super Admin  
  **Pre:** license upload, NPI/DEA, ID‑proofing  
  **Flow:** credentials → 2FA setup → eRx vendor binding → EPCS tokens

- **UC‑ID‑04: Attorney/Funder Workspace Provisioning**  
  **Actors:** Attorney/Funder Admin, Super Admin  
  **Flow:** org signup → DPA/BAA as applicable → user invites → case scoping

### B) Intake & Screening
- **UC‑IN‑01: AI Conversational Intake (Self‑Pay)**  
  **Actors:** Patient  
  **Pre:** authenticated; consented  
  **Flow:** demographics → CC/HPI → screeners (PHQ‑9/GAD‑7/ASRS triggers) → meds/allergies → risk  
  **Alt:** high‑risk → emergency guidance + escalation queue; incomplete intake → save & resume  
  **Data:** structured JSON, scores, flags  
  **Notify/Audit:** intake summary to provider; risk flag audit

- **UC‑IN‑02: LOP Intake (Attorney/Patient)**  
  **Actors:** Attorney/Case Mgr/Patient  
  **Flow:** accident details, counsel, insurer, LOP upload → funding request packet

- **UC‑IN‑03: Therapy Matching Preferences**  
  **Actors:** Patient  
  **Flow:** goals, modality, language, availability → ranked matches

### C) Routing, Scheduling & Telehealth
- **UC‑SC‑01: Smart Routing & Scheduling**  
  **Actors:** Patient, Scheduler  
  **Pre:** licensure/state coverage; modality preference  
  **Flow:** show slots → hold w/ card (self‑pay) or LOP approval → confirm  
  **Alt:** waitlist; provider time‑off; timezone mismatch  
  **Data:** appt, provider, hold token  
  **Notify:** SMS/email confirms; calendar invites

- **UC‑SC‑02: Reschedule/Cancel/No‑Show**  
  **Actors:** Patient, Scheduler  
  **Flow:** policy‑aware change; fees auto‑applied; no‑show workflow  
  **Alt:** medical exception; auto‑forgive rules

- **UC‑SC‑03: Televisit Connection Management**  
  **Actors:** Patient, Provider, Support  
  **Flow:** device check → join → in‑visit chat/screen‑share  
  **Alt:** low bandwidth fallback (audio), PSTN dial‑in; failover room

### D) Clinical Encounter & Documentation
- **UC‑CL‑01: Initial Psychiatric Evaluation**  
  **Actors:** Provider  
  **Pre:** completed intake  
  **Flow:** review intake → interview → MSE → diagnosis → plan  
  **Data:** note template; attachments  
  **Alt:** insufficient data → follow‑up task; safety plan template

- **UC‑CL‑02: Follow‑Up / Medication Management**  
  **Flow:** interval history → vitals/self‑report → med adj/refills → counseling → AVS

- **UC‑CL‑03: Therapy Session**  
  **Flow:** agenda → intervention notes → homework → outcomes update

- **UC‑CL‑04: Note Assist & Coding Aids**  
  **Flow:** draft from intake/transcript → clinician edits → finalize → lock  
  **Alt:** AI disabled per patient preference → manual

### E) ePrescribing, PDMP & Labs
- **UC‑RX‑01: eRx (Non‑Controlled)**  
  **Actors:** Provider  
  **Flow:** med search → dose/sig → interaction/allergy check → pharmacy select → send  
  **Alt:** pharmacy change; eRx bounce retry

- **UC‑RX‑02: EPCS (Controlled)**  
  **Pre:** EPCS setup; PDMP policy  
  **Flow:** ID token + 2FA → PDMP check logged → send  
  **Alt:** PDMP outage (document attestation & retry)

- **UC‑RX‑03: Refill Request**  
  **Actors:** Patient  
  **Flow:** request → rules (visit recency) → provider queue → approve/deny with reasons

- **UC‑LB‑01: Lab Order & Results**  
  **Flow:** order (Lipid, A1c, EKG, etc.) → external lab → result ingestion → abnormal alert → provider sign‑off → patient notified

### F) Documentation, Consents & Records
- **UC‑DO‑01: E‑Sign Consents**  
  **Actors:** Patient  
  **Flow:** HIPAA, telehealth, financial, controlled substance agreement, LOP consent  
  **Alt:** Part 2 sensitive sections with selective ROI

- **UC‑DO‑02: ROI & Records Export**  
  **Actors:** Patient, Attorney, Admin  
  **Flow:** request → validate → generate packet → release with watermark + audit

### G) Payments, Pricing & Payouts
- **UC‑PM‑01: Self‑Pay Checkout**  
  **Actors:** Patient  
  **Flow:** price shown → card capture → receipt → refund rules  
  **Alt:** HSA/FSA; failure + dunning

- **UC‑PM‑02: Provider Payouts**  
  **Actors:** Billing, Provider  
  **Flow:** earnings calc (split/tier) → statement → ACH  
  **Alt:** dispute → reconciliation task

- **UC‑LOP‑01: Lien Funding Approval**  
  **Actors:** Funder Analyst  
  **Flow:** review packet → approve/decline/conditional → set cap/terms

- **UC‑LOP‑02: Periodic Report & Ledger Update**  
  **Actors:** Provider, Billing, Attorney  
  **Flow:** report template → attorney portal → ledger accrual

- **UC‑LOP‑03: Settlement Reconciliation**  
  **Actors:** Billing, Attorney, Funder  
  **Flow:** invoice → settlement amount → payoff → write‑offs/shortfall policy

### H) Messaging, Tasks & Coordination
- **UC‑MS‑01: Secure Messaging**  
  **Actors:** Patient↔Provider, Attorney↔MSO  
  **Flow:** thread → attachments → SLA timers → escalation

- **UC‑TK‑01: Taskboard (Carevo)**  
  **Actors:** All internal roles  
  **Flow:** auto‑create tasks (PDMP check, missing doc, abnormal lab) → assign → track

### I) Analytics, Reporting & Quality
- **UC‑AN‑01: Clinical Outcomes Dashboard**  
  **Actors:** Clinical Director  
  **Flow:** PHQ‑9/GAD‑7/ASRS trends; remission; safety events

- **UC‑AN‑02: Operational KPIs**  
  **Actors:** Admin  
  **Flow:** time‑to‑appt, show rate, utilization, refill turnaround, response SLAs

- **UC‑AN‑03: Compliance & Access Logs**  
  **Actors:** Compliance  
  **Flow:** export logs; quarterly review; attestations

### J) Content & Growth (Non‑PHI)
- **UC‑MK‑01: Landing Experiments**  
  **Actors:** Marketing  
  **Flow:** A/B tests → conversion tracking (cookie‑consented)

- **UC‑MK‑02: SEO Content Publishing**  
  **Actors:** Content  
  **Flow:** TMS/med education posts → structured data → accessibility checks

---

## CTQ by Role (KPIs & SLAs)

### Patient (Self‑Pay)
- **Time to first appointment:** ≤ **48 hours** (p95) from completed intake.
- **Booking conversion rate:** ≥ **35%** from intake completion to confirmed slot (baseline; iterate).
- **Televisit connectivity success:** ≥ **99.0%** session join success; reconnect within 60s if dropped.
- **Refill turnaround:** ≤ **2 business days** (p95) for eligible requests.
- **Support response:** ≤ **15 min** during clinic hours via chat for urgent access issues.
- **Accessibility:** WCAG 2.1 AA; readable at 6–8th grade.

### Injury Patient (LOP)
- **Case approval notification:** within **3 business days** from complete LOP packet.
- **Status transparency:** portal shows **next appointment**, **remaining cap**, **documents** in < 3 clicks.

### Attorney / Case Manager
- **Document availability SLA:** initial eval report within **2 business days** post‑visit; periodic reports per cadence (e.g., q30d).
- **Ledger accuracy:** < **0.5%** variance vs internal AR.
- **Portal uptime:** ≥ **99.9%** monthly.

### Lien Funder Analyst
- **Funding decision turnaround:** ≤ **5 business days** (p95) once packet complete.
- **Exposure tracking:** real‑time ledger, export in **CSV/PDF** within 10s.

### Provider (Prescriber)
- **Clicks to finalize note:** ≤ **25** for initial eval; ≤ **15** for follow‑up (target).
- **Visit‑to‑eRx cycle time:** ≤ **5 minutes** median.
- **PDMP check latency:** ≤ **30 seconds** (where API; portal screenshot workflow ≤ 2 minutes).
- **No‑show waste:** auto‑filled documentation & task closure within **1 minute**.

### Provider (Therapist)
- **Session note completion:** within **24 hours** (p95).
- **Homework delivery:** within **5 minutes** post‑session.

### Scheduler / Care Coordinator
- **First contact SLA (triage flags):** ≤ **10 minutes** during hours.
- **Waitlist fill rate:** ≥ **25%** of cancellations rebooked within **24 hours**.

### Billing & Finance (MSO)
- **Payout accuracy:** **100%** of statements tie to ledger; disputes resolved ≤ **5 business days**.
- **Refund cycle:** ≤ **3 business days** to customer bank.
- **Settlement posting:** within **2 business days** of attorney remittance.

### Compliance & Privacy Officer
- **Audit completeness:** **100%** of eRx/PDMP actions logged with user/time/IP.
- **Access reviews:** quarterly; remediate variances within **10 business days**.
- **Incident response:** notify internal leadership within **1 hour**; regulatory timelines per state/federal rules.

### Clinical Director / QA
- **Chart audit coverage:** ≥ **10%** of encounters monthly; CAPA tracked to closure.
- **Safety events:** zero tolerance for untriaged C‑SSRS “high‑risk” flags; documented escalation in **<15 minutes**.

### Marketing/Content (Non‑PHI)
- **Core Web Vitals:** LCP ≤ **2.5s**, CLS ≤ **0.1** on marketing pages.
- **Attribution integrity:** cookie consent and anonymized analytics verified quarterly.

### Super Admin
- **Change management:** feature flag rollouts with **< 0.1%** incident rate; rollback ≤ **5 minutes**.

---

## Edge‑Case Catalog & Controls

1. **High suicide risk flagged in intake (C‑SSRS):**  
   Control: Hard stop to booking → emergency guidance + warm transfer; notify on‑call clinician; audit.
2. **Patient under 18 without guardian:**  
   Control: Age gate → guardian workflow; block eRx until verified.
3. **Video fails to connect:**  
   Control: auto diagnostics; audio fallback; PSTN dial‑in; reschedule credit per policy.
4. **PDMP outage / no API access:**  
   Control: in‑portal attestation + screenshot upload; queued retry; audit tag.
5. **EPCS token failure:**  
   Control: backup 2FA method; revoke/rehydrate keys; support playbook.
6. **Pharmacy rejects eRx (formulary/stock):**  
   Control: alternate pharmacy flow; patient notification; provider task.
7. **Duplicate patient record:**  
   Control: match/merge with human review; prevent cross‑merge of Part 2 data.
8. **No‑show / late cancel:**  
   Control: fees per policy; auto messaging; slot released to waitlist.
9. **Attorney change mid‑case:**  
   Control: revoke old access; transfer LOP; ledger continuity checks.
10. **Funder denies/lowers cap:**  
    Control: care plan re‑scope; notify all parties; informed consent about limits.
11. **Settlement shortfall:**  
    Control: write‑off policy engine; approvals; updated statements to provider.
12. **Data subject request (access/delete):**  
    Control: HIPAA/Part 2 compliant response; immutable legal record retained per policy.
13. **Breach / suspected compromise:**  
    Control: incident runbook; isolate credentials; notify per regulatory timelines.

---

## RACI for Critical Processes

| Process | R | A | C | I |
|---|---|---|---|---|
| Initial eval & diagnosis | Provider | Clinical Director | Scheduler | Patient |
| EPCS prescription | Provider | Clinical Director | Compliance | Patient |
| PDMP verification | Provider | Compliance | Scheduler | Patient |
| LOP funding approval | Funder Analyst | Funder Admin | Attorney, Billing | Patient, Provider |
| Settlement reconciliation | Billing | CFO/Finance Lead | Attorney, Funder | Provider |
| Access audits | Compliance | Compliance | Super Admin | All |
| Payout runs | Billing | Finance Lead | Provider | Admin |

---

## Acceptance Criteria Snapshots

### AC‑RX‑01: EPCS Send (Controlled Substance)
- Given provider has active EPCS + 2FA and patient has a valid encounter, when provider signs Rx, then system must: (a) log PDMP check/attestation, (b) require successful 2FA, (c) deliver receipt from eRx partner, (d) store immutable audit entry.

### AC‑SC‑02: No‑Show Policy Enforcement
- When patient fails to join within grace window, system marks no‑show, applies fee if configured, releases slot to waitlist, and triggers patient+provider notifications.

### AC‑IN‑03: ADHD Attention Complaint → ASRS Trigger
- If intake contains attention complaints, ASRS v1.1 must be auto‑presented; scores saved and surfaced in provider pre‑chart.

### AC‑LOP‑04: Periodic Attorney Report
- Within 2 business days of cadence date, system generates templated PDF from latest encounters and posts to portal with notification.

---

## Post‑MVP Backlog & Dependencies
- **Insurance claims** (837/835) and RCM workflows.
- **Employer/B2B** onboarding; PHI‑lite ROI dashboards.
- **Device integrations** (BP, HRV, sleep trackers) for vitals at scale.
- **FHIR‑based interoperability** for external EHRs.
- **Group therapy** scheduling & billing.
- **Spanish‑first counseling content** with culturally adapted scripts.
- **Clinical rules engine** for smarter triage/refill policies.

> Ready for conversion into user stories + Jira epics. Provide feedback on SLA targets or any role we should add/remove.

