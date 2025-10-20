from flask import Flask, request, jsonify, Response

app = Flask(__name__)

movies = []
next_id = 1

def find_movie(movie_id: int):
    return next((m for m in movies if m["id"] == movie_id), None)

@app.route("/movies", methods=["GET"])
def list_movies():
    return jsonify(movies), 200

@app.route("/movies", methods=["POST"])
def create_movie():
    global next_id
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "nume" not in payload:
        return Response(status=400)

    name = payload.get("nume")
    if not isinstance(name, str) or not name.strip():
        return Response(status=400)

    movie = {"id": next_id, "nume": name.strip()}
    movies.append(movie)
    next_id += 1
    return jsonify(movie), 201

@app.route("/movie/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "nume" not in payload:
        return Response(status=400)

    name = payload.get("nume")
    if not isinstance(name, str) or not name.strip():
        return Response(status=400)

    movie = find_movie(movie_id)
    if movie is None:
        return Response(status=404)

    movie["nume"] = name.strip()
    return jsonify(movie), 200

@app.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if movie is None:
        return Response(status=404)
    return jsonify(movie), 200

@app.route("/movie/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id: int):
    global movies
    movie = find_movie(movie_id)
    if movie is None:
        return Response(status=404)
    movies = [m for m in movies if m["id"] != movie_id]
    return jsonify({"status": "deleted"}), 200

@app.route("/reset", methods=["DELETE"])
def reset():
    global movies, next_id
    movies = []
    next_id = 1
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
