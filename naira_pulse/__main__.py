"""Allow `python -m naira_pulse` to launch the offline demo."""

from naira_pulse.demo import main

if __name__ == "__main__":
    raise SystemExit(main())
