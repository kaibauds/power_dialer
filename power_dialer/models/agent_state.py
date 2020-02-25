from db_impl.dynamo import AgentState


def exists():
    return AgentState.exists()


def get_all():
    return AgentState.scan()


def create_table():
    AgentState.create_table(read_capacity_units=10, write_capacity_units=10)


def init(agent_id):
    if query(agent_id) is None:
        agent_state = AgentState(agent_id)
        agent_state.save()
        return agent_state


def query(agent_id):
    try:
        return AgentState.get(agent_id)
    except Exception:
        return None


def delete(agent_id):
    try:
        AgentState.get(agent_id).delete()
    except Exception:
        print("Agent might not exist")


def update(state, attr_dict):
    for key, value in attr_dict.items():
        setattr(state, key, value)
    return state
