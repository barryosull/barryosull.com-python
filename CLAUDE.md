# Python Development Guidelines

## Code Style & Standards
- Follow PEP 8 style guide strictly
- Use type hints for all function signatures and class attributes
- Maximum line length: 88 characters (Black formatter standard)
- Prefer f-strings over .format() or % formatting

## Documentation Style
- Module-level docstrings: Only at the top of files to describe the module's purpose
- Class/Function docstrings: AVOID redundant docstrings - let type hints and clear naming speak for themselves
- Only add docstrings when they provide non-obvious information that type hints cannot convey
- No redundant "Args", "Returns", "Raises" sections when the signature is self-explanatory
- Test functions: No docstrings - the function name should describe what's being tested
- Inline comments: Only for complex algorithms or non-obvious business logic

## Project Structure
- Use `src/` layout for packages
- Separate business logic from interface code (CLI, web, etc.)
- Keep configuration in a dedicated module
- Use dependency injection for better testability

## Dependencies & Tools
- Package management: `pyproject.toml` with modern build backend (setuptools, hatchling, or poetry)
- Formatting: Black + isort
- Linting: ruff (replaces flake8, pylint, isort)
- Type checking: mypy with strict mode
- Testing: pytest with pytest-cov for coverage

## Testing
- Aim for >80% test coverage
- Write unit tests for all business logic
- Use fixtures for test data and setup
- Mock external dependencies (APIs, databases, file I/O)
- Test both success and failure paths

## Code Quality
- No commented-out code in commits
- No print statements in production code (use logging)
- Handle exceptions explicitly, avoid bare `except:`
- Use context managers (`with` statements) for resources
- Prefer composition over inheritance

## Modern Python Practices
- Use Python 3.10+ features (match/case, union types with |)
- Leverage dataclasses or Pydantic models for data structures
- Use pathlib.Path instead of os.path
- Async/await for I/O-bound operations
- Use structural pattern matching where appropriate

## Dependencies
- Keep dependencies minimal and well-justified
- Pin major versions in pyproject.toml
- Use virtual environments always
- Regular dependency updates and security audits

## External Documentation
- README with setup, usage, and examples
- API documentation for public interfaces
- Keep docs close to code to ensure they stay updated
- Avoid documentation that duplicates what the code already expresses

## Git Practices
- Conventional commits format
- Feature branches with descriptive names
- Small, focused commits
- Never commit secrets or .env files