# Contributing to Freenet Headless Deploy

Thank you for contributing to **Freenet Headless Deploy**!

## Development & Testing

This repository intentionally uses **zero third-party Python dependencies** (standard library only) so that AI agents and developers can run it immediately on any macOS or Linux environment.

### Running the Test Suite

```bash
python3 -m unittest discover -s tests -v
```

### Submitting Pull Requests

1. Fork the repository and create a branch from `main`.
2. Add or update unit tests in `tests/test_deploy_script.py` for any new path rewriting or CLI functionality.
3. Verify all tests pass locally via `make test`.
4. Open a Pull Request with a clear summary of changes.

## License

By contributing to this repository, you agree that your contributions will be licensed under the [MIT License](./LICENSE).
