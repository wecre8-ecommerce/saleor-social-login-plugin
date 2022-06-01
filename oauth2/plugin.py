import json

from django.shortcuts import redirect

from saleor.account.models import User

from saleor.graphql.views import GraphQLView
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField
from saleor.plugins.models import PluginConfiguration
from oauth2.graphql.schema import schema
from oauth2.utils import PluginOAuthProvider, normalize_config, parse_providers_str


class OAuth2Plugin(BasePlugin):
    name = "social-login"  # tackle saleor/saleor#8873
    PLUGIN_ID = "social-login"
    PLUGIN_NAME = "OAuth2 support"
    DEFAULT_ACTIVE = False
    PLUGIN_DESCRIPTION = "A plugin that adds support for OAuth2 and currently supports Google, Facebook and Apple."  # noqa: E501
    CONFIGURATION_PER_CHANNEL = False

    DEFAULT_CONFIGURATION = [
        {"name": "providers", "value": ""},
        {
            "name": "google_client_id",
            "value": None,
        },
        {
            "name": "google_client_secret",
            "value": None,
        },
        {"name": "facebook_client_id", "value": None},
        {"name": "facebook_client_secret", "value": None},
        {"name": "apple_client_id", "value": None},
        {"name": "apple_team_id", "value": None},
        {"name": "apple_key_id", "value": None},
        {"name": "apple_private_key", "value": None},
        {"name": "apple_redirect_url", "value": None},
    ]

    CONFIG_STRUCTURE = {
        "providers": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Provider names comma separated",
            "label": "Enabled services",
        },
        "google_client_id": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Your Google Client ID",
            "label": "Google Client ID",
        },
        "google_client_secret": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Google Your Client secret",
            "label": "Google Client Secret",
        },
        "facebook_client_id": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Your Facebook Client ID",
            "label": "Facebook Client ID",
        },
        "facebook_client_secret": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Google Your Client secret",
            "label": "Facebook Client Secret",
        },
        "apple_client_id": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Your Apple Client ID",
            "label": "Apple Client ID",
        },
        "apple_team_id": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Your Apple team ID",
            "label": "Apple Team ID",
        },
        "apple_key_id": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Your Apple private key ID",
            "label": "Apple KID",
        },
        "apple_private_key": {
            "type": ConfigurationTypeField.SECRET_MULTILINE,
            "help_text": "Your Apple private key",
            "label": "Apple Private Key",
        },
        "apple_redirect_url": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "The storefront Apple redirect URL",
            "label": "Apple Redirect URL",
        },
    }

    @classmethod
    def validate_plugin_configuration(cls, plugin_configuration: "PluginConfiguration"):
        config = normalize_config(plugin_configuration.configuration)
        providers = parse_providers_str(config["providers"])

        if plugin_configuration.active and providers:
            for provider in providers:
                PluginOAuthProvider.from_config(
                    provider, plugin_configuration.configuration
                )

    def webhook(self, request, path, previous_value):
        if path == "/webhook/apple":
            user_data = request.POST.get("user")
            if user_data:
                user_data = json.loads(user_data)
                email = user_data.get("email")
                name = user_data.get("name")
                User.objects.get_or_create(
                    email=email,
                    defaults={
                        "is_active": True,
                        "last_name": name.get("lastName"),
                        "first_name": name.get("firstName"),
                    },
                )
            config = normalize_config(self.get_plugin_configuration(self.configuration))
            return redirect(
                f"{config.get('apple_redirect_url', '/')}"
                f"?code={request.POST.get('code')}"
                f"&state={request.POST.get('state')}"
            )
        request.app = self
        view = GraphQLView.as_view(schema=schema)
        return view(request)
