# Contributing

Thanks for improving this project.

## Before opening a pull request

1. Keep the raw survey CSV out of version control.
2. Regenerate cleaned outputs with the local pipeline script if you change the cleaning logic.
3. Run the test suite before submitting changes.
4. Update the README when the workflow or outputs change.

## Development checks

```bash
python -m compileall scripts tests
python -m unittest discover -s tests
python scripts/pipeline.py
```

## Privacy rules

- Do not commit names, emails, phone numbers, school identifiers, timestamps, or free-text responses that can identify a student.
- Prefer aggregated figures and anonymized exports in the public repository.