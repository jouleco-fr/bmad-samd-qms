# bmad-samd-qms

A Claude Code plugin that scaffolds a regulation-aligned **SaMD Quality Management System** and
wires it into every [BMAD](https://github.com/bmad-ai/bmad-method) workflow automatically.

Covers: **FDA 21 CFR 820 · IEC 62304 · ISO 14971 · EU MDR 2017/745 · FDA §524B**

## What it does

1. Asks ~10 questions about your device (name, FDA/EU MDR class, IEC 62304 safety class, PHI handling)
2. Scaffolds a complete `qms/` directory with pre-populated, regulation-aligned templates
3. Wires QMS constraints (DoD, risk register, SOUP register, traceability) into every BMAD workflow
   so Claude builds your software under medical device discipline automatically

## Install

```bash
# From GitHub (once this repo is pushed):
claude plugin install https://github.com/YOUR_ORG/bmad-samd-qms.git

# Or from this local directory:
claude plugin install /home/christophe/ClaudeAI/bmad-samd-qms
```

## Use

In any Claude Code session with BMAD installed:

```
/qms-init          # first time: wizard + scaffold + BMAD wiring
/qms-init validate # check QMS completeness
/qms-update        # apply template updates after plugin upgrade
```

## What gets scaffolded

```
qms/
├── definition-of-done.md
├── constraints-register.md
├── soup-register.md
├── open-items.md
├── regulatory/  (intended-use, IEC 62304, FDA classification, GSPR, cybersecurity, CEP, PMS, submission ToC)
├── risk/        (risk-management-file, risk-register)
├── requirements/(traceability)
└── architecture/(component-map)
```

## Standards covered

| Standard | Coverage |
|---|---|
| IEC 62304:2006+A1:2015 | Software lifecycle file, safety class decision, SOUP register |
| ISO 14971:2019 | Risk management file, risk register, benefit-risk analysis |
| ISO 13485:2016 | QMS structure, DoD, traceability (SOPs flagged as [QMS] gaps) |
| EU MDR 2017/745 | GSPR checklist, clinical evaluation plan, PMS plan |
| FDA 21 CFR 820 | Classification rationale, predicate analysis, cybersecurity file |
| FD&C Act §524B | Cybersecurity file template |
| IEC 62366-1 | Usability engineering flagged in risk controls |

## Read more

See [HOWTO.md](HOWTO.md) for the full regulatory context, filling guide, and maintenance instructions.

## License

MIT — provided as a starting scaffold. Not regulatory advice. Have a regulatory affairs professional
review all documents before submission.
