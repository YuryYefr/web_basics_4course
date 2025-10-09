import sqlite3

from flask import Flask, request, g
from ariadne import load_schema_from_path, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerGraphiQL
from database import Database
from resolvers import query, mutation

DATABASE = 'test_db.sqlite'

app = Flask(__name__)
app.secret_key = 'My super secret key'

# Load schema from file and create an executable schema
type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, query, mutation)

# Create an instance of GraphiQL for the playground
explorer_html = ExplorerGraphiQL().html(None)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Use the application context to initialize the database
with app.app_context():
    conn = get_db()
    try:
        Database.get_users(conn)
    except sqlite3.OperationalError:
        Database.populate_database(conn)
    close_db()


@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    # Serve the GraphiQL IDE on GET requests
    return explorer_html, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # Get the GraphQL query from the POST request
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value={"db": get_db()}
    )
    return result, 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)
