# cg-stats
[![Code Climate](https://codeclimate.com/github/18F/cg-stats-scripts/badges/gpa.svg)](https://codeclimate.com/github/18F/cg-stats-scripts)

cg-stats is a script that will collect and print stats about a specified cloud foundry environment.

## Setup

```
pip install requests
pip install numpy
```

## Init

Set the following envionment variables

- `STATS_API_URL` The base Cloud Foundry API URL
- `STATS_USERNAME` The username for an admin account
- `STATS_PASSWORD` The password for the admin account

## Running

- Run `python main.py`
