[![License: BSL-1.1](https://img.shields.io/badge/License-BSL--1.1-blue.svg)](https://opensource.org/licenses/BSL-1.0)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: MPL-2.0](https://img.shields.io/badge/License-MPL--2.0-orange.svg)](https://www.mozilla.org/en-US/MPL/2.0/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://python.org)
[![Stan](https://img.shields.io/badge/Stan-Bayesian-B1261C.svg)](https://mc-stan.org)
[![MiniZinc](https://img.shields.io/badge/MiniZinc-Constraint-2E7D32.svg)](https://www.minizinc.org)
[![Evidence or Silence](https://img.shields.io/badge/Protocol-Evidence%20or%20Silence-black.svg)](#)

# bio-semantics

**基因表達語義建模管線 (خط أنابيب النمذجة الدلالية للتعبير الجيني)**

Gene-expression semantic modeling pipeline — Stan + MiniZinc + cDNA sequencing visualizer with immutable artifact provenance, PTM verification, and RPG/JCL integration templates.

Authors: Ahmad Ali Parr, Jessica L. Williams (SNAPKITTYWEST)

---

## Architecture

```
                BIOLOGICAL OBSERVATIONS
                         │
                         ▼
                cDNA EXPRESSION DATA
                         │
                         ▼
                ┌─────────────────┐
                │ DATA VALIDATION │  ← semantics.py (10 validator rules)
                └────────┬────────┘
                         │
                         ▼
                GENE EXPRESSION
                         │
                         ▼
                ┌─────────────────┐
                │   STAN MODEL    │  ← Bayesian inference
                │ priors          │
                │ likelihood      │
                │ posterior       │
                └────────┬────────┘
                         │
                         ▼
                 POSTERIOR STATE
                         │
                         ▼
                ┌─────────────────┐
                │ MINIZINC MODEL  │  ← Constraint reasoning
                │ constraints     │
                │ optimization    │
                └────────┬────────┘
                         │
                         ▼
                COMPUTATIONAL RESULT
                         │
                         ▼
                ┌─────────────────┐
                │ VISUALIZER      │  ← dashboard.html (8 panels)
                │ HTML + CSS      │
                └────────┬────────┘
                         │
                         ▼
                HUMAN-READABLE MODEL
```

---

## Repository Structure

```
bio-semantics/
├── src/
│   ├── semantics.py           Validator + PTM parity machine
│   ├── test_semantics.py      Unit tests (6 test classes)
│   └── dashboard.html         8-panel semantic report viewer
├── spec/
│   ├── types.ts               TypeScript type definitions (bio-semantics/1.0.0)
│   ├── contract.md            Gate 1 integration contract
│   └── system_prompt.md       Agent system prompt specification
└── templates/
    ├── workflow.rpgle          RPG workflow coordinator (IBM i)
    └── vault.jcl              JCL vault archival template
```

---

## Quantity Kinds

| Kind | Meaning | 意義 (المعنى) |
|------|---------|--------------|
| observed | Measurement with source record locator | 觀測值 (القيمة المرصودة) |
| inferred | Posterior with model/run references and uncertainty | 推斷值 (القيمة المستنتجة) |
| derived | Deterministic transformation with algorithm references | 衍生值 (القيمة المشتقة) |
| predicted | Unobserved modeled quantity | 預測值 (القيمة المتوقعة) |
| constrained | Declared relation or solver result | 約束值 (القيمة المقيدة) |
| encoded | Representation with codec identifier | 編碼值 (القيمة المرمزة) |
| executed | Actual execution event with run evidence | 執行事件 (حدث التنفيذ) |

---

## Validator Rules

1. Reject unsupported versions, unknown discriminants, duplicate IDs
2. Require exactly one of present value or missing reason
3. Raw counts: canonical unsigned decimal only
4. Decimal quantities: reject NaN/infinity, require units
5. Require sample/gene references to resolve
6. Reject inferred/predicted/constrained labeled as observed
7. Preserve excluded rows with explicit inclusion map
8. Missing source bytes block verified-ingestion claims
9. Synthetic-origin propagation through every descendant
10. Never create model-results merely because a process was scheduled

---

## PTM: ptm-bit-parity/1

| State | Read | Write | Move | Next |
|-------|------|-------|------|------|
| q_even | 0 | 0 | R | q_even |
| q_even | 1 | 1 | R | q_odd |
| q_odd | 0 | 0 | R | q_odd |
| q_odd | 1 | 1 | R | q_even |
| q_even | _ | 0 | Stay | q_accept |
| q_odd | _ | 1 | Stay | q_accept |

For input length n: exactly n+1 transitions, constant auxiliary storage.

---

## Run Tests

```bash
cd src && python -m pytest test_semantics.py -v
```

---

## Gated Phases

| Gate | What | Status |
|------|------|--------|
| 1. Contract | Contracts accepted, encodings documented, provenance validated | Ready for review |
| 2. Engine | Stan/MiniZinc/Quipper sources exist, native validation recorded | Not started |
| 3. Integration | All panels rendered, WORM loaded, governance preserved | Not started |

---

## License

This project is released under a **trilicense** model. You may choose any one of the following:

| License | SPDX | Link |
|---------|------|------|
| Boost Software License 1.0 | BSL-1.1 | [LICENSE-BSL](https://opensource.org/licenses/BSL-1.0) |
| GNU Affero General Public License v3 | AGPL-3.0 | [LICENSE-AGPL](https://www.gnu.org/licenses/agpl-3.0) |
| Mozilla Public License 2.0 | MPL-2.0 | [LICENSE-MPL](https://www.mozilla.org/en-US/MPL/2.0/) |

Unauthorized cloud SaaS redistribution without source disclosure is prohibited under all three licenses.

---

SnapKitty West / SNAPKITTYWEST — Evidence or Silence — 2026
