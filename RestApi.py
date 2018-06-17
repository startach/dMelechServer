from flask import Flask, request, jsonify
from ExtendedJSONEncoder import ExtendedJSONEncoder
from SynagogueModel import Synagogue, get_synagogue, update_synagogue, \
    search_synagogue, create_synagogue

app = Flask(__name__)
app.json_encoder = ExtendedJSONEncoder


@app.route('/synagogue/', methods=['GET', 'POST', 'PUT'])
def synagogue():
    if request.method == 'GET':
        params = {}
        for a,v in request.args.items():
            params[a] = v
        res = get_synagogue(**params)
        if res:
            return jsonify(res), 200
        return None, 400

    elif request.method == 'POST':
        j = request.get_json()
        res = create_synagogue(j)
        if res[0]:
            return jsonify(True), 200
        elif res[0] == False and res[1] == 'no_location':
            return jsonify(False), 206
        return jsonify(False), 500

    elif request.method == 'PUT':
        syn_id = request.args['syn_id']
        j = request.get_json()
        res = update_synagogue(syn_id, j)
        if res:
            return jsonify(res), 200
        return jsonify(False), 500


if __name__ == '__main__':
    app.run(debug=True)
