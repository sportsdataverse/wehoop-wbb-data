"""Builder: ESPN WBB player crosswalk (ESPN <-> NCAA athletes).

Thin entrypoint. The build lives in ``wbb_data_build``; this file exists so the
directory listing is the pipeline and each dataset is runnable on its own.

Numbered 15 to match ``R/wbb_15_player_crosswalk_creation.R`` -- the R chain had this
stage and python did not, which the R/Python parity test now prevents.
"""

from wbb_data_build.entrypoint import run

DATASET = "player_crosswalk"

if __name__ == "__main__":
    raise SystemExit(run(DATASET))
