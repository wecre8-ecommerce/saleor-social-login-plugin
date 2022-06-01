from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.middleware.csrf import _get_new_csrf_token

from saleor.account import events as account_events
from saleor.account import search
from saleor.core.jwt import create_access_token, create_refresh_token
from saleor.plugins.base_plugin import BasePlugin
from oauth2.consts import providers_config_map
from oauth2.graphql import enums
from oauth2.providers import Provider

User = get_user_model()


def get_scope(provider_name):
    return providers_config_map[provider_name].scope


def normalize_config(config):
    return {item["name"]: item["value"] for item in config}


def get_oauth2_info(provider, config):
    result = {}

    for key, val in config.items():
        if key.startswith(provider):
            prefix_length = len(f"{provider}_")
            new_key = key[prefix_length:]
            result.update(
                {
                    new_key: val,
                }
            )

    return result


def get_user_tokens(user):
    access_token = create_access_token(user)
    csrf_token = _get_new_csrf_token()
    refresh_token = create_refresh_token(user, {"csrfToken": csrf_token})

    return {
        "token": access_token,
        "csrf_token": csrf_token,
        "refresh_token": refresh_token,
    }


def get_user_data(user):
    return {
        "email": user.email,
        "last_name": user.last_name,
        "first_name": user.first_name,
    }


def parse_providers_str(providers):
    result = []

    providers = providers.split(",")
    providers = list(filter_truthy(providers))

    for provider in providers:
        result.append(provider.strip().lower())

    return result


def filter_truthy(iter):
    return filter(bool, iter)


def get_or_create_user(request, email, first_name="", last_name=""):
    user, created = User.objects.get_or_create(email=email)
    user.is_active = True
    user.last_name = last_name if last_name else user.last_name
    user.first_name = first_name if first_name else user.first_name
    user.search_document = search.prepare_user_search_document_value(
        user, attach_addresses_data=False
    )
    user.save()
    account_events.customer_account_created_event(user=user)
    request.plugins.customer_created(customer=user)

    return created, user


class PluginOAuthProvider:
    @classmethod
    def from_plugin(cls, name, plugin: BasePlugin):
        return cls.from_config(name, plugin.configuration)

    @classmethod
    def from_config(cls, name, config):
        provider_cls = providers_config_map[name]
        config = normalize_config(config)
        config = get_oauth2_info(name, config)
        provider: Provider = provider_cls(**config)

        try:
            provider.validate()
        except TypeError as e:
            raise ValidationError(e, code=enums.OAuth2ErrorCode.OAUTH2_ERROR.value)

        return provider
