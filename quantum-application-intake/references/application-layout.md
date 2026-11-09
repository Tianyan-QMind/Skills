# Generated Quantum Application Layout

Every generated application uses `generated_apps/<application_slug>/`. The slug is lowercase
kebab-case. All manifest paths are POSIX paths relative to the application root; absolute paths,
`..`, and symlink escapes are forbidden.

```text
generated_apps/<application_slug>/
├── application_manifest.json       # current unversioned machine contract
├── evidence_report.md              # only when external research/route comparison is needed
├── plan.md                         # durable implementation decision contract
├── README.md                       # final Simplified-Chinese user guide
├── final_report.md                 # final Simplified-Chinese result report
├── algorithm/
├── scripts/
├── tests/
├── models/                         # conditional
├── backend/                        # runnable_app only
├── frontend/standalone/            # runnable_app only
└── artifacts/
    ├── run_history.jsonl           # automatically appended by command tools
    ├── results/                    # raw and algorithm-specific machine results
    ├── plots/                      # conditional
    └── logs/                       # conditional, only when diagnostically useful
```

Producers create directories only when they have real content. Do not create empty placeholder
directories. Data analysis and verification return bounded direct summaries; they do not publish
per-role Markdown reports. `run_history.jsonl` records sanitized execution facts and excludes
stdout, stderr, environment variables, credentials, and account information.

An application is ready for handoff when expected source, Chinese final documentation, and tests
exist and the run history describes actual local checks. This does not certify deployment,
TianYan execution, scientific validity, or quantum advantage.
