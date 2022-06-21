import graphene
from graphene_federation import build_schema
from oauth2.graphql.mutations import (SocialLogin, SocialLoginByAccessToken,
                                      SocialLoginConfirm)
from saleor.graphql.account.types import User
from saleor.graphql.core.federation.schema import build_federated_schema


class Query(graphene.ObjectType):
    social_login = SocialLogin.Field()
    social_login_by_token = SocialLoginByAccessToken.Field()
    social_login_confirm = SocialLoginConfirm.Field()


class Mutation(graphene.ObjectType):
    social_login = SocialLogin.Field()
    social_login_confirm_mobile = SocialLoginByAccessToken.Field()
    social_login_confirm_web = SocialLoginConfirm.Field()


schema = build_schema(Query, Mutation)
