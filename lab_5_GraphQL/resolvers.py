from ariadne import QueryType, MutationType
from database import Database

# Create type instances for Query and Mutation
query = QueryType()
mutation = MutationType()


# Define the query resolvers
@query.field("allUsers")
def resolve_all_users(obj, info):
    db = info.context["db"]
    users = Database.get_users(db)
    # Convert Row objects to dictionaries
    return [dict(u) for u in users]


@query.field("user")
def resolve_user(obj, info, id):
    db = info.context["db"]
    user = Database.get_user(db, id)
    return dict(user) if user else None


# Define the mutation resolvers
@mutation.field("createUser")
def resolve_create_user(obj, info, username, occupation):
    db = info.context["db"]
    new_user_id = Database.add_user(db, username, occupation)
    new_user = Database.get_user(db, new_user_id)
    return dict(new_user)


@mutation.field("updateUser")
def resolve_update_user(obj, info, id, occupation):
    db = info.context["db"]
    Database.update_user(db, id, occupation)
    updated_user = Database.get_user(db, id)
    return dict(updated_user) if updated_user else None


@mutation.field("deleteUser")
def resolve_delete_user(obj, info, id):
    db = info.context["db"]
    Database.delete_user(db, id)
    # The client-side will just see null for the deleted user
    return None
