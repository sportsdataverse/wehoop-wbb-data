"""Builder: ESPN WBB player box scores.

Thin entrypoint. The build lives in ``wbb_data_build``; this file exists so the
directory listing is the pipeline and each dataset is runnable on its own.
"""

from wbb_data_build.entrypoint import run

DATASET = "player_box"

if __name__ == "__main__":
    raise SystemExit(run(DATASET))
