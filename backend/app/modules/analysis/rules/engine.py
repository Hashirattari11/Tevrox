"""Rules engine public API.

Re-exports rule data and the rule runner from rules_data.
"""

from app.modules.analysis.rules.rules_data import (
    RULES_VERSION,
    get_rules,
    run_rules,
)

__all__ = ["RULES_VERSION", "get_rules", "run_rules"]
