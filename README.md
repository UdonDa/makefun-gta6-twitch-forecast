# makefun-gta6-twitch-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/UdonDa/makefun-gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/UdonDa/makefun-gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

An offline forecaster for GTA VI's launch-day Twitch viewers: given the first hour's viewer count and a set of comparable past game launches bundled in each case, it predicts five quantiles (5/25/50/75/95%) for every remaining hour of the release day. For each comparable launch it builds the log-ratio curve against its own first hour, weights launches by how close their first-hour scale is, takes weighted empirical quantiles per hour, smooths the median and the spread separately over a three-hour window, and applies a spread factor of 0.95 (chosen by leave-one-out cross-validation over 28 historical launches, where it scored a mean log pinball loss of 0.271 against the persistence baseline's 0.351). Python standard library only; no network, no model calls, deterministic.

## Run it

```sh
# Put case files (<id>.in) in the input directory, then:
MAKEFUN_INPUT_DIR=/input MAKEFUN_OUTPUT_DIR=/output python3 main.py
# Writes <id>.out for each case into the output directory.
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=59tnrs35&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
