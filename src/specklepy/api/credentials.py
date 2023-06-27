import os
from typing import List, Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from specklepy.api.models import ServerInfo
from specklepy.core.helpers import speckle_path_provider
from specklepy.logging import metrics
from specklepy.logging.exceptions import SpeckleException
from specklepy.transports.sqlite import SQLiteTransport

# following imports seem to be unnecessary, but they need to stay 
# to not break the scripts using these functions as non-core
from specklepy.core.api.credentials import (UserInfo, Account, StreamWrapper, 
                                            get_account_from_token,
                                            get_local_accounts as core_get_local_accounts)

def get_local_accounts(base_path: Optional[str] = None) -> List[Account]:
    """Gets all the accounts present in this environment

    Arguments:
        base_path {str} -- custom base path if you are not using the system default

    Returns:
        List[Account] -- list of all local accounts or an empty list if
        no accounts were found
    """
    accounts = core_get_local_accounts(base_path)

    metrics.track(
        metrics.SDK,
        next(
            (acc for acc in accounts if acc.isDefault),
            accounts[0] if accounts else None,
        ),
        {"name": "Get Local Accounts"}
    )

    return accounts

def get_default_account(base_path: Optional[str] = None) -> Optional[Account]:
    """
    Gets this environment's default account if any. If there is no default,
    the first found will be returned and set as default.
    Arguments:
        base_path {str} -- custom base path if you are not using the system default

    Returns:
        Account -- the default account or None if no local accounts were found
    """
    accounts = core_get_local_accounts(base_path=base_path)
    if not accounts:
        return None

    default = next((acc for acc in accounts if acc.isDefault), None)
    if not default:
        default = accounts[0]
        default.isDefault = True
    metrics.initialise_tracker(default)

    return default
    