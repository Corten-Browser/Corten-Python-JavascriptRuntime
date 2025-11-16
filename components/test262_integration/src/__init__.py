"""
Test262 Integration Component

Provides comprehensive Test262 conformance suite integration for Corten JavaScript Runtime.

Main exports:
- Test262Harness: Core harness for test execution
- Test262Runner: Automated test runner with filtering and parallel execution
- Reporter: Report generation (HTML, JSON, Markdown, JUnit)
- CI integration utilities for GitHub Actions and regression detection
"""

from components.test262_integration.src.harness import (
    Test262Harness,
    Test262Error
)
from components.test262_integration.src.runner import (
    Test262Runner,
    ConfigError
)
from components.test262_integration.src.reporter import (
    Reporter,
    BaselineNotFoundError
)
from components.test262_integration.src.ci_integration import (
    create_github_actions_workflow,
    save_workflow,
    detect_regressions,
    update_baseline_if_approved,
    check_baseline_approval,
    get_exit_code,
    format_ci_summary,
    create_status_badge_url,
    generate_ci_comment
)

__all__ = [
    # Harness
    'Test262Harness',
    'Test262Error',

    # Runner
    'Test262Runner',
    'ConfigError',

    # Reporter
    'Reporter',
    'BaselineNotFoundError',

    # CI Integration
    'create_github_actions_workflow',
    'save_workflow',
    'detect_regressions',
    'update_baseline_if_approved',
    'check_baseline_approval',
    'get_exit_code',
    'format_ci_summary',
    'create_status_badge_url',
    'generate_ci_comment',
]

__version__ = '0.1.0'
