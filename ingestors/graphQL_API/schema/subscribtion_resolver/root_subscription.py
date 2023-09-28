from ariadne import SubscriptionType


root_subscription = SubscriptionType()

@root_subscription.field("environmentData")
def resolve_environment_data(root, info):
    return {}