from setuptools import setup

setup(
    name="oauth2",
    version="0.1.0",
    packages=["oauth2"],
    package_dir={"oauth2": "oauth2"},
    description="Oauth2 API client",
    entry_points={
        "saleor.plugins": ["oauth2 = oauth2.plugin:OAuth2Plugin"],
    },
)
