from flask import Flask, request, jsonify, redirect
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "MySecretKey"
jwt = JWTManager(app)


@app.route('/', methods=['GET', 'POST'])
def hello_and_redirect_to_login():
    if request.method == 'GET':
        return jsonify({'message': 'just a redirect, make POST on login'}, 200)
    return redirect('/login')


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != '':
        access_token = create_access_token(identity=username)
        refresh_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token})
    return {'message': 'Bad username or password'}, 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
