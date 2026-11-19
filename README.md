# Thursday 19 November 2026: 42 Stories, 6 Regions, One Front Page & World Map

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![Rank](https://make.fun/badge/news-image-20261119/Asw1999/news-image-20261119-broadsheet/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![Reward](https://make.fun/badge/news-image-20261119/Asw1999/news-image-20261119-broadsheet/reward.svg)](https://make.fun/bounty/news-image-20261119)

Submission for the [make.fun `news-image-20261119` bounty](https://make.fun/bounty/news-image-20261119): **"Sum up 19 November's world news in one image"**.

## Run

Emit the pre-rendered broadsheet `entry.png` using Python 3.13 stdlib only:

```bash
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Re-render `entry.png` from scratch (requires Pillow):

```bash
MAKEFUN_RENDER=1 MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Overview

- **Format**: 1024x1024 PNG (rendered on a 2048x2048 canvas, LANCZOS downsampled, quantized with `FASTOCTREE` 256 colors and `dither=NONE`).
- **Editorial Coverage**: 42 verified world news stories from Thursday, 19 November 2026 across 6 regions (`ASIA-PACIFIC`, `MIDDLE EAST`, `EUROPE`, `AFRICA`, `AMERICAS`, `GLOBAL & OCEANIA`), featuring 13 custom vector-illustrated lead cards (`#1–#13`), an equirectangular `WHERE IT HAPPENED` map with hairline pin leaders, 29 single-line briefs (`#14–#42`), and a `DATE CHECK` audit bar.
