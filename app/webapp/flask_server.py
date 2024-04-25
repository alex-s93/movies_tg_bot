from os import getenv

from flask import Flask, render_template, request
from app.service import AppService
from dotenv import load_dotenv

app = Flask(__name__)
service = AppService()


@app.route('/movie')
def movie():
    movie_id = request.args.get('id')
    movie_data = service.get_film_by_id(movie_id)
    return render_template('movie.html', movie=movie_data)


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True, host=getenv('localhost'), port=getenv('port'))
