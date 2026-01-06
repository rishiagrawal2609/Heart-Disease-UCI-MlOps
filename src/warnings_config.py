"""
Warning configuration to suppress MLflow/Pydantic deprecation warnings

Import this module early in your scripts to suppress common warnings
from MLflow and Pydantic dependencies.
"""

import warnings

# Suppress urllib3 OpenSSL warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

# Suppress Pydantic deprecation warnings from MLflow
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince20.*")
warnings.filterwarnings("ignore", message=".*Pydantic V1 style.*")
warnings.filterwarnings("ignore", message=".*Support for class-based `config`.*")
warnings.filterwarnings("ignore", message=".*Valid config keys have changed.*")
warnings.filterwarnings("ignore", message=".*Field.*has conflict with protected namespace.*")

# Suppress Pydantic validator deprecation warnings
warnings.filterwarnings("ignore", message=".*@validator.*is deprecated.*")
warnings.filterwarnings("ignore", message=".*@root_validator.*is deprecated.*")
warnings.filterwarnings("ignore", message=".*migrate to Pydantic V2.*")

