# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable, Optional, Any, Tuple

from azure.core.credentials import AccessToken
from .._internal import AadClient
from .._internal.get_token_mixin import GetTokenMixin


class ClientAssertionCredential(GetTokenMixin):
    """Authenticates a service principal with a JWT assertion.

    This credential is for advanced scenarios. :class:`~azure.identity.ClientCertificateCredential` has a more
    convenient API for the most common assertion scenario, authenticating a service principal with a certificate.

    :param str tenant_id: ID of the principal's tenant. Also called its "directory" ID.
    :param str client_id: The principal's client ID
    :param func: A callable that returns a string assertion. The credential will call this every time it
        acquires a new token.
    :paramtype func: Callable[[], str]

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud (which is the default).
        :class:`~azure.identity.AzureAuthorityHosts` defines authorities for other clouds.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(
            self,
            tenant_id: str,
            client_id: str,
            func: Callable[[], str],
            **kwargs: Any
    ) -> None:
        self._func = func
        self._client = AadClient(tenant_id, client_id, **kwargs)
        super(ClientAssertionCredential, self).__init__(**kwargs)

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def _acquire_token_silently(
        self, *scopes: str, **kwargs: Any
    ) -> Tuple[Optional[AccessToken], Optional[int]]:
        return self._client.get_cached_access_token(scopes, **kwargs), None

    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        assertion = self._func()
        token = self._client.obtain_token_by_jwt_assertion(scopes, assertion, **kwargs)
        return token
