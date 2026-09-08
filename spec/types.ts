type QuantityKind =
  | "observed" | "inferred" | "derived" | "predicted"
  | "constrained" | "encoded" | "executed";

type Datum<T> =
  | { status: "present"; value: T }
  | {
      status: "missing";
      reason: "not_measured" | "not_reported" | "failed_qc" | "unknown";
      detail?: string;
    };

type ArtifactRef =
  | { status: "available"; artifactId: string; sha256: string }
  | { status: "unavailable"; reason: string };

interface SourceLocator {
  artifact: ArtifactRef;
  recordLocator: string;
}

interface ExpressionObservation {
  schemaVersion: "bio-semantics/1.0.0";
  observationId: string;
  datasetId: string;
  sampleId: string;
  geneId: string;
  condition: Datum<string>;
  timepoint: Datum<{ value: string; unit: string }>;
  replicate: Datum<string>;
  batch: Datum<string>;
  cellType: Datum<string>;
  measurement:
    | {
        kind: "raw_read_count";
        quantityKind: "observed";
        unit: "reads";
        value: Datum<string>;
      }
    | {
        kind: "normalized_expression";
        quantityKind: "derived";
        unit: string;
        value: Datum<string>;
        transformation: ArtifactRef;
      };
  quality: Array<{
    name: string;
    unit: string;
    value: Datum<string>;
    quantityKind: "observed" | "derived";
    source: SourceLocator;
  }>;
  source: SourceLocator;
  origin:
    | { kind: "measurement" }
    | {
        kind: "synthetic_fixture";
        fixtureId: string;
        excludedFromScientificConclusions: true;
      };
}
