from sheer_audit.governance import build_governance_bundle, build_governance_issues
from sheer_audit.model.schema import Finding, RepoInfo, RepoModel


def _sample_model() -> RepoModel:
    return RepoModel(
        repo=RepoInfo(root=".", name="demo"),
        findings=[
            Finding(code="ARCH-LAYER", severity="ERROR", file="src/a.py", line=10, message="violation"),
            Finding(code="ARCH-LAYER", severity="WARN", file="src/a.py", line=14, message="warning"),
            Finding(code="SEC-SECRETS", severity="CRITICAL", file="src/b.py", line=7, message="secret"),
            Finding(code="STYLE", severity="INFO", file="src/c.py", line=3, message="style"),
        ],
        metrics={"files": 3},
    )


def test_build_governance_issues_orders_by_score_then_severity() -> None:
    issues = build_governance_issues(_sample_model().findings)

    assert [item.code for item in issues] == ["SEC-SECRETS", "ARCH-LAYER", "STYLE"]
    assert issues[0].priority_score == 13
    assert issues[1].priority_score == 11


def test_build_governance_bundle_is_deterministic() -> None:
    report = _sample_model()

    bundle_a = build_governance_bundle(report)
    bundle_b = build_governance_bundle(report)

    assert bundle_a.report_fingerprint == bundle_b.report_fingerprint
    assert bundle_a.issues_markdown == bundle_b.issues_markdown
    assert "Fingerprint do relatório fonte" in bundle_a.issues_markdown
