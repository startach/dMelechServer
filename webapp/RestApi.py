from flask import Flask, request, jsonify
from ExtendedJSONEncoder import ExtendedJSONEncoder
from SynagogueModel import get_synagogue, update_synagogue, \
    create_synagogue, search_synagogue
from flask_cors import CORS

app = Flask(__name__)
app.json_encoder = ExtendedJSONEncoder
cors = CORS(app, resources={r"/": {"origins": ""}})


@app.route('/synagogue/<string:syn_id>', methods=['GET', 'PUT'])
def synagogue(syn_id):
    if request.method == 'GET':
        res = get_synagogue(syn_id)
        if res:
            return jsonify({
                "status": "OK",
                "content": res
            }), 200
        return jsonify({
            "status": "ERROR",
            "content": {}
        }), 400

    else:
        j = request.get_json()
        res = update_synagogue(syn_id, j)
        if res:
            return jsonify(res), 200
        return jsonify(False), 500


@app.route('/synagogue/', methods=['POST'])
def synagogue_post():
    j = request.get_json()
    res = create_synagogue(j)
    if res:
        return jsonify(True), 200
    return jsonify(False), 500


# final
@app.route('/synagogue/search', methods=['POST'])
def synagogue_search():
    j = request.get_json()
    res = search_synagogue(j)
    if res is not False:
        return jsonify({
            "status": "OK",
            "content": res
        }), 200
    return jsonify({
        "status": "ERROR",
        "content": {}
    }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True, use_reloader=False, threaded=True)
