from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)


movies_df = pd.read_csv(r"C:\Users\pauli\Desktop\Zaawansowane_programowanie1\python_api\data\movies.csv")
links_df = pd.read_csv(r"C:\Users\pauli\Desktop\Zaawansowane_programowanie1\python_api\data\links.csv")
ratings_df = pd.read_csv(r"C:\Users\pauli\Desktop\Zaawansowane_programowanie1\python_api\data\ratings.csv")
tags_df = pd.read_csv(r"C:\Users\pauli\Desktop\Zaawansowane_programowanie1\python_api\data\tags.csv")



class Movie:
    def __init__(self, movieId, title, genres):
        self.movieId = movieId
        self.title = title
        self.genres = genres

    def to_dict(self):
        return self.__dict__



@app.route("/", methods=["GET"])
def home():
    return jsonify({"hello": "world"})



@app.route("/movies", methods=["GET"])
def get_movies():
    movies = [Movie(row["movieId"], row["title"], row["genres"]).to_dict() for _, row in movies_df.iterrows()]
    return jsonify(movies)



@app.route("/links", methods=["GET"])
def get_links():
    return jsonify(links_df.to_dict(orient="records"))



@app.route("/ratings", methods=["GET"])
def get_ratings():
    return jsonify(ratings_df.to_dict(orient="records"))



@app.route("/tags", methods=["GET"])
def get_tags():
    return jsonify(tags_df.to_dict(orient="records"))



@app.route("/all", methods=["GET"])
def get_all():
    return jsonify({
        "movies": movies_df.to_dict(orient="records"),
        "links": links_df.to_dict(orient="records"),
        "ratings": ratings_df.to_dict(orient="records"),
        "tags": tags_df.to_dict(orient="records")
    })



if __name__ == "__main__":
    app.run(debug=True)
