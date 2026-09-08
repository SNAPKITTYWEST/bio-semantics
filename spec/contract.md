# Bio-Semantics Integration Contract — Gate 1

**Version:** bio-semantics/1.0.0
**Status:** Gate 1 candidate — contract specification only. Not implemented or tested.

---

## Integration Pipeline

```
Python → Validation → Normalization → Model Inputs → Stan → MiniZinc → Quipper → Artifact Validation → Visualization/Reporting
```

Each stage result carries:

| Field | Type |
|-------|------|
| run_id, stage_id, semantic_stage | identifiers |
| status | blocked / not_run / running / succeeded / failed / timeout |
| reason | string |
| input_artifact_ids[], output_artifact_ids[] | references |
| tool_name, tool_version, command_arguments[], working_directory | execution |
| started_at, ended_at, exit_code | timing |
| stdout_artifact_id, stderr_artifact_id | logs |
| random_seed | value / not_applicable / unavailable |

Solver outcome is separate from process status:

```
solver_outcome: feasible | optimal | infeasible | unknown | timeout | failed | not_run
```

A successful process exit is insufficient evidence of successful inference, a feasible solution, convergence, or quantum execution.

---

## Quantity Kinds

| Kind | Meaning |
|------|---------|
| observed | Measurement with source record locator |
| inferred | Posterior quantity with model/run references and uncertainty |
| derived | Deterministic transformation with algorithm and input references |
| predicted | Unobserved modeled quantity with model/run references |
| constrained | Declared permitted relation or solver result |
| encoded | Representation with semantic source, codec identifier, and bit length |
| executed | Actual execution event with run evidence |

---

## Validator Rules (10)

1. Reject unsupported versions, unknown discriminants, contradictory variants, empty identifiers, duplicate observation IDs
2. Require exactly one of present value or missing reason
3. Raw counts: canonical unsigned decimal only (no negatives, fractions, exponents, whitespace)
4. Decimal quantities: reject NaN/infinity, require declared units
5. Require sample/gene references to resolve
6. Reject inferred/predicted/constrained quantities labeled observed
7. Preserve excluded rows with explicit inclusion map
8. Missing source bytes block verified-ingestion claims
9. Synthetic-origin propagation through every descendant artifact
10. Never create model-result objects merely because a process was scheduled

---

## Binary Semantics Profiles

- **u32-checked/1**: unsigned 32-bit, big-endian, range 0..4294967295; overflow traps
- **i32-checked/1**: signed two's-complement, big-endian; overflow traps; MIN_INT/-1 traps

---

## PTM: ptm-bit-parity/1

Input alphabet: {0,1}. Tape alphabet: {0,1,_}. States: {q_even, q_odd, q_accept, q_reject}.

| State | Read | Write | Move | Next |
|-------|------|-------|------|------|
| q_even | 0 | 0 | R | q_even |
| q_even | 1 | 1 | R | q_odd |
| q_odd | 0 | 0 | R | q_odd |
| q_odd | 1 | 1 | R | q_even |
| q_even | _ | 0 | Stay | q_accept |
| q_odd | _ | 1 | Stay | q_accept |

For input length n: exactly n+1 transitions, n+1 tape cells, constant auxiliary storage.

---

## Gated Phases

1. **Contract gate**: Contracts and validators accepted; encodings/arithmetic/PTM documented; provenance validated
2. **Engine gate**: Stan/MiniZinc/Quipper sources exist; native validation evidence recorded; failures preserved
3. **Integration/release gate**: All panels rendered with lineage; WORM loaded first; governance checks preserved

---

## Acceptance Tests (specified, not run)

| Case | Expected |
|------|----------|
| Present raw count "0" | Valid observed zero |
| Missing count with not_measured | Valid missing; never zero-filled |
| Missing variant also contains value | Invalid |
| Raw count "-1", "1.5", "1e3" | Invalid |
| Count above native backend range | Adapter rejects conversion |
| Normalized measurement labeled observed | Invalid |
| Posterior relabeled observed | Invalid |
| Missing source/hash | Provenance incomplete |
| Synthetic input -> posterior -> report | Synthetic marker propagated |
| Two records with duplicate identity | Invalid |
| u32 maximum plus one | Overflow fault |
| Integer divide by zero | Arithmetic fault |
| Encode/decode present zero versus missing | Distinct round trips |
| PTM "", "0", "1", "1011" | Output 0, 0, 1, 1; transitions 1, 2, 2, 5 |
| Fortran summation | Expected sum=5050 |
