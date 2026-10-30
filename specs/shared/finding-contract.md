# Finding Contract

## Purpose

Define a consistent, evidence-based format for findings produced by advisors,
reviewers, and supervisors.

Domain specifications may add fields or stricter requirements, but they must not
weaken this contract.

## Finding Types

Classify each observation as one of:

- **Confirmed defect**: Available evidence establishes incorrect or unsafe
  behavior.
- **Potential risk**: Evidence shows a credible failure scenario, but important
  runtime or architectural context remains unknown.
- **Test gap**: Important behavior is not adequately verified. A test gap is not
  proof of a functional defect.
- **Suggestion**: A nonessential improvement with a clear engineering benefit.

Positive observations and review limitations are not findings and should be
reported separately.

## Required Fields

Every finding must include:

1. **Severity**: Critical, High, Medium, or Low.
2. **Type**: Confirmed defect, potential risk, test gap, or suggestion.
3. **Title**: A concise description of the problem.
4. **Location**: File and line number when available.
5. **Evidence**: The relevant behavior, code path, or observed tool output.
6. **Failure scenario**: The conditions that trigger the problem.
7. **Impact**: The expected technical or user consequence.
8. **Recommendation**: A concrete direction for remediation.
9. **Confidence**: High, medium, or low.

When an exact location is unavailable, explain why and identify the nearest
relevant component.

## Severity

### Critical

A realistic failure can cause catastrophic impact, such as unrestricted remote
code execution, broad compromise of sensitive systems, irreversible widespread
data loss, or a complete failure of a critical safety boundary.

### High

A realistic failure can cause significant unauthorized access, sensitive data
exposure, persistent corruption, major outage, or failure of a core application
workflow.

### Medium

A failure has meaningful but limited impact, requires additional conditions, or
substantially reduces reliability, security, or maintainability.

### Low

A localized weakness, minor correctness issue, or defense-in-depth improvement
with limited immediate impact.

Severity must reflect demonstrated context and impact rather than the name of a
vulnerability or rule.

## Confidence

### High

The behavior is directly established by code flow, reproducible output, or a
relevant deterministic test.

### Medium

The evidence supports the finding, but some runtime behavior, configuration, or
external dependency has not been verified.

### Low

The scenario is plausible but important evidence is missing. Low-confidence
items should normally be reported as investigation needs or limitations rather
than actionable defects.

## Evidence Rules

- Verify that referenced files, symbols, and lines exist.
- Trace enough of the execution path to support the claimed behavior.
- Consider surrounding validation, authorization, error handling, and other
  compensating controls.
- Do not infer runtime configuration without evidence.
- Do not claim that tests or commands passed unless they ran successfully.
- Do not report a missing test as proof that implementation behavior is broken.
- Deduplicate findings that describe the same root cause.
- Preserve meaningful uncertainty rather than overstating impact.

## Report Structure

A consolidated report should contain:

1. Executive summary.
2. Critical and high findings.
3. Medium and low findings.
4. Test gaps and suggestions.
5. Positive observations, when useful.
6. Coverage: which specialists and validation mechanisms were used.
7. Limitations and unresolved uncertainty.

If no material findings are supported, state that explicitly. Do not invent
findings to populate the report.
