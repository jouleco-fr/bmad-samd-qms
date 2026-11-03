# How-To: SaMD QMS for BMAD Projects

A practical guide to using the `bmad-samd-qms` plugin — what the regulatory framework
requires, how the QMS is structured, and how to maintain it while building software with BMAD.

---

## Section 1 — Regulatory context

### What makes software a medical device?

Software is a medical device (SaMD — Software as a Medical Device) when it is intended to be
used for a medical purpose **without being part of a hardware medical device**. The key question
is *purpose*: does the software diagnose, treat, monitor, predict, or manage a patient condition,
or is it purely administrative / operational?

**In the US (FDA):** Software that meets the device definition in 21 CFR §201(h) is regulated
under the FD&C Act. SaMD typically falls under Class I (low risk), II (moderate), or III (high),
depending on risk level and the availability of a predicate device.

**In the EU (MDR):** Software is a medical device if it meets the device definition in Article 2(1)
of EU MDR 2017/745. Classification uses the MDCG 2019-11 guidance and Rule 11:
- Class I — no harm if software fails or performs poorly
- Class IIa — low/medium risk (most clinical data management SaMD lands here)
- Class IIb — medium/high risk (diagnostic or monitoring outputs)
- Class III — high risk (life-sustaining, implantable logic)

### The IEC 62304 safety class — the most consequential decision

IEC 62304 requires you to assign a **software safety class** before development begins:

| Class | Definition | Required V&V depth |
|---|---|---|
| **A** | No injury or damage to health possible | Basic: unit tests, documentation |
| **B** | Non-serious injury possible (reversible, no permanent harm) | Moderate: unit + integration tests, detailed design, architecture |
| **C** | Serious injury or death possible | Full: all Class B requirements + system testing, anomaly management, formal risk control verification |

The class drives how much testing evidence you need, what coverage thresholds apply, and
whether a full detailed design (SDD) is required. **When in doubt, choose B over A.**
The class must be confirmed by the ISO 14971 risk analysis — they are interdependent.

### Key standards in scope

| Standard | What it governs |
|---|---|
| **IEC 62304:2006+A1:2015** | Software development lifecycle |
| **ISO 14971:2019** | Risk management |
| **ISO 13485:2016** | Quality management system (QMS/SOPs) |
| **IEC 62366-1:2015** | Usability engineering |
| **IEC 81001-5-1:2021** | Health software cybersecurity |
| **FDA 21 CFR Part 820** | US Quality System Regulation |
| **EU MDR 2017/745** | EU regulatory framework |
| **FD&C Act §524B** | US premarket cybersecurity requirements |

### US vs EU — key differences

| Aspect | US (FDA) | EU (MDR) |
|---|---|---|
| Submission | 510(k) / De Novo / PMA | Technical Documentation + Notified Body review (IIa+) |
| Risk management | FDA expects ISO 14971 | ISO 14971 explicitly required |
| Software lifecycle | FDA Software Guidance 2023 | IEC 62304 explicitly required |
| Cybersecurity | §524B (FD&C Act) | GSPR Annex I + MDCG guidance |
| Clinical evidence | Substantial equivalence (510k) | Clinical evaluation (CEP + CER) |
| Post-market | MDR Part 803, 21 CFR 822 | MDR Article 83, Annex III, PSUR |

---

## Section 2 — Using this plugin

### Install once per workstation

```bash
# From a GitHub URL (once pushed):
claude plugin install https://github.com/jouleco-fr/bmad-samd-qms.git

# Or from a local directory:
claude plugin install /path/to/bmad-samd-qms
```

This registers the `qms-init` and `qms-update` skills globally on your workstation.
They become available in every Claude Code session.

### Bootstrap a new project (once per project)

In any Claude Code session with BMAD installed, run:

```
/qms-init
```

The wizard asks:
1. Device name (the marketed product name)
2. Manufacturer name
3. One-sentence intended use
4. Clinical domain
5. FDA class (II-510k / II-denovo / III-PMA / I-exempt / none)
6. EU MDR class (I / IIa / IIb / III / none)
7. IEC 62304 software safety class (A / B / C)
8. PHI handling (yes/no)
9. Clinician-confirmed output (yes/no)
10. Target jurisdictions (US / EU / CA / UK)
11. Source control system
12. Artifact/dependency repository

After you answer, the skill:
- Scaffolds a `qms/` directory in your project with all templates populated
- Registers the `samd` BMAD module in `_bmad/config.yaml`
- Patches `_bmad/custom/config.toml` so every BMAD workflow loads QMS constraints automatically

### What gets created

```
qms/
├── README.md                        ← QMS overview and ID conventions
├── definition-of-done.md            ← Universal completion bar (wired into dev-story)
├── constraints-register.md          ← Hard design inputs (CON-*)
├── soup-register.md                 ← SOUP dependency register
├── open-items.md                    ← Open items and deferred decisions
├── regulatory/
│   ├── intended-use.md             ← Intended use statement (root of the dossier)
│   ├── iec-62304-software-file.md  ← Software lifecycle documentation
│   ├── fda-classification-rationale.md
│   ├── gspr-checklist.md           ← EU MDR Annex I
│   ├── cybersecurity-file.md       ← FDA §524B / IEC 81001-5-1
│   ├── clinical-evaluation-plan.md ← EU MDR CEP
│   ├── pms-plan.md                 ← Post-Market Surveillance plan
│   └── submission-toc.md           ← Submission table of contents
├── risk/
│   ├── risk-management-file.md     ← Governing ISO 14971 file
│   └── risk-register.md            ← Hazard index
├── requirements/
│   └── traceability.md             ← Traceability requirements (REQ-TRACE-*)
└── architecture/
    └── component-map.md            ← Component decomposition
```

Files containing `{{` tokens are stubs waiting to be filled in.
Run `/qms-init validate` to see which files still have unfilled placeholders.

### BMAD workflow wiring

After setup, these BMAD skills automatically load QMS context:

| Skill | QMS files loaded |
|---|---|
| `bmad-create-prd` | definition-of-done, constraints-register, intended-use |
| `bmad-create-architecture` | definition-of-done, constraints-register, traceability |
| `bmad-create-story` | definition-of-done, constraints-register, traceability, risk-register |
| `bmad-dev-story` | definition-of-done, constraints-register, soup-register, risk-register |
| `bmad-code-review` | definition-of-done, traceability |
| `bmad-retrospective` | definition-of-done, open-items |

You do not need to remind Claude about QMS requirements in these sessions — they are loaded automatically.

---

## Section 3 — Maintaining the QMS

### Fill in the stubs — in order

Work through the stubs in this order (each one unlocks the next):

1. **`intended-use.md`** — The foundation. Everything else derives from it.
   Get RA sign-off before writing the classification rationale.

2. **`fda-classification-rationale.md` / `gspr-checklist.md`** — Confirm your class.
   Do a predicate search (US) or MDCG 2019-11 classification exercise (EU).

3. **`risk/risk-management-file.md`** — The governing document.
   Hazard analysis confirms your IEC 62304 safety class. Without this, the class is provisional.

4. **`regulatory/iec-62304-software-file.md`** — Software lifecycle map.
   Cross-reference architecture artifacts and test reports as they are built.

5. **`soup-register.md`** — Add every dependency. One row per library.
   Keep it in sync with your build file (pom.xml, package.json, requirements.txt, etc.).

6. **`regulatory/cybersecurity-file.md`** — Required if you are a "cyber device" (§524B).
   Coordinate with the risk file — security threats link directly to safety risks.

7. **`regulatory/clinical-evaluation-plan.md`** and **`pms-plan.md`** — Required for EU MDR.
   The CEP defines how you will gather clinical evidence; the PMS plan defines post-market monitoring.

### What to update after each story

After each story is done:

- If a new SOUP item was added: add it to `soup-register.md`
- If a new risk was identified: add it to `risk/risk-register.md` and update `risk-management-file.md`
- If a design decision changed: add/update an ADR in `decisions/`
- If an `OPEN-*` item was resolved: close it in `open-items.md`
- If a new open item was found: add it to `open-items.md`

The `definition-of-done.md` section 7 ("Build, CI & documentation") makes these updates mandatory — stories are not Done until QMS docs are current.

### Running `/qms-init validate`

At any time, run `/qms-init validate` to get a readiness report:

- **COMPLETE**: file exists, no `{{` tokens remaining
- **NEEDS_FILL**: file exists but still has unfilled placeholder tokens
- **MISSING**: required file does not exist

The validate action also checks jurisdiction-specific requirements (e.g. FDA files if `jurisdiction=US`,
GSPR/CEP/PMCF files if `jurisdiction=EU`).

### Updating the plugin

When a new version of `bmad-samd-qms` is released:

```bash
# Update the plugin files (new templates, new skills)
claude plugin update bmad-samd-qms

# Apply template changes to your project (skips customized files)
/qms-update
```

Files you have customized (i.e. `{{` tokens replaced with real content) are never overwritten.
Only stubs that still contain placeholder tokens get updated.

### Getting RA / regulatory review

This QMS is a **technical scaffold**, not regulatory advice. Before relying on any document
for a regulatory submission:

1. Have a regulatory affairs professional (RA) review all files in `qms/regulatory/`
2. Have a clinical expert review `risk/risk-management-file.md`
3. For EU MDR Class IIa+: engage a Notified Body early (they review technical documentation)
4. For US: strongly consider an FDA Pre-Submission (Q-Sub) before investing in the full 510(k)

The `open-items.md` file tracks which regulatory gaps require expert attention.

---

## Appendix — ID convention reference

| Prefix | Meaning |
|---|---|
| `CON-<AREA>-NN` | Constraint / design input |
| `ADR-NNNN` | Architecture Decision Record |
| `REQ-<AREA>-NN` | Derived requirement |
| `RISK-NN` | Risk register item (ISO 14971) |
| `OPEN-NN` | Open item (stub, deferred decision, not-started area) |
| `FR-NN` | Functional requirement (from PRD) |
| `SEC-N` | Security requirement / control |
