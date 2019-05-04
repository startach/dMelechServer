#!/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from ExtendedJSONEncoder import ExtendedJSONEncoder
from SynagogueMongo import get_synagogue_by_id, update_synagogue, create_synagogue, search_synagogue
from flask_cors import CORS

app = Flask(__name__)
app.json_encoder = ExtendedJSONEncoder

CORS(app)


@app.route('/synagogue/<string:syn_id>', methods=['GET'])
def get_synagogue(syn_id):
    try:
        res = get_synagogue_by_id(syn_id)
        if res:
            return jsonify({
                "status": "OK",
                "content": res
            }), 200
        return jsonify({
            "status": "ERROR",
            "content": {res}
        }), 400
    except Exception as e:
        return jsonify(e), 500


@app.route('/synagogue/<string:syn_id>', methods=['PUT'])
def put_synagogue(syn_id):
    try:
        j = request.get_json()
        res = update_synagogue(syn_id, j)
        if res:
            return jsonify(res), 200
        return jsonify(False), 500
    except Exception as e:
        return jsonify(e), 500


@app.route('/synagogue', methods=['POST'])
def post_synagogue():
    try:
        j = request.get_json()
        res = create_synagogue(j)
        if res[0]:
            return jsonify(res), 200

        return jsonify(res[1]), 400
    except Exception as e:
        return jsonify(e), 500


@app.route('/synagogue/search', methods=['POST'])
def post_synagogue_search():
    try:
        j = request.get_json()
        res = search_synagogue(j)
        if res[0] is not False:
            return jsonify({
                "status": "OK",
                "data": res[1]
            }), 200
        return jsonify({
            "status": "ERROR",
            "data": str(res[1])
        }), 400
    except Exception as e:
        return jsonify(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
