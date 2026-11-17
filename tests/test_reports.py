import pandas as pd
import pytest

from adewi.reports import generate_executive_summary_markdown, generate_latex_table


def test_reports_generator(tmp_path):
    df = pd.DataFrame({"Province": ["Eastern", "Southern"], "Lead_Weeks": [6.2, 5.8]})
    tex = generate_latex_table(df, "Lead Time Summary", "tab:lead_time")
    assert "\\begin{table}" in tex
    assert "Lead_Weeks" in tex

    summary = generate_executive_summary_markdown(
        {"mean_lead_weeks": 6.1, "success_rate": 0.88},
        out_path=tmp_path / "summary.md",
    )
    assert "6.1 weeks" in summary
    assert "88.0%" in summary
