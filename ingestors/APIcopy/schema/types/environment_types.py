import graphene

class IndoorEnvironmentData(graphene.ObjectType):
    opRoom = graphene.String()
    co2 = graphene.Int()
    # time = graphene.String()
    # co2 = graphene.Float()
    # door_state = graphene.String()
    # humidity = graphene.Float()
    # illuminance = graphene.Float()
    # noise = graphene.Float()
    # op_room = graphene.String(source='op_room')
    # pressure = graphene.Float()
    # temperature = graphene.Float()
    # uv = graphene.Float()
    

