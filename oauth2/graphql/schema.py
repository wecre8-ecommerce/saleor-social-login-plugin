import graphene

from saleor.graphql.account.types import User
from saleor.graphql.core.federation.schema import build_federated_schema
from oauth2.graphql.mutations import SocialLogin, SocialLoginByAccessToken, SocialLoginConfirm

class Query(graphene.ObjectType):
    social_login = SocialLogin.Field()
    social_login_by_token = SocialLoginByAccessToken.Field()
    social_login_confirm = SocialLoginConfirm.Field()

class Mutation(graphene.ObjectType):
    social_login = SocialLogin.Field()
    social_login_confirm_mobile = SocialLoginByAccessToken.Field()
    social_login_confirm_web = SocialLoginConfirm.Field()


schema = build_federated_schema(Query, Mutation, types=[User])
