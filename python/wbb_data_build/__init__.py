"""Python producer for the ESPN WBB release datasets.

Parity port of ``wehoop-wbb-data/R/espn_wbb_*_creation.R``. Reshapes the sibling
``wehoop-wbb-raw`` per-game JSON into season-level parquet/csv + manifest and
publishes to the ``espn_womens_college_basketball_*`` release tags. R is retained
as the byte-parity oracle.
"""

__all__ = ["config", "ingest", "io", "build", "publish", "reshapers"]
