# council/config.py — shim that re-exports from the main package
# This allows `from council.config import ...` to work as a submodule import
from council import (
    CouncilConfig,
    CouncilMember,
    DEFAULT_MEMBERS,
    ensure_member_dirs,
    load_council_config,
    save_council_config,
)
