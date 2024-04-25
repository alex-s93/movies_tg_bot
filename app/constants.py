# messages

class Messages:
    unknown_command = "Unfortunately I don't understand that. Please, use my menu to do something"
    enter_new_amount = "Enter a new default amount value:"
    enter_keywords = "Enter keywords for search separated by whitespace:"
    enter_name = "Enter name for search:"
    enter_actors = "Please enter the actors' full names separated by commas (format - Firstname Lastname):"
    success_new_amount = "New value was successfully saved! Now {} movies will be shown as result for you search."
    digits_invalid = "You entered invalid value. Please, use only positive digits"
    keywords_invalid = "You entered invalid value. Please, use only alphabetic symbols and digits"
    select_option = "Choose one of the following options:"
    select_year = "Select a year:"
    selected_year = "Applied year: {}"
    entered_keywords = "Applied keywords: {}"
    entered_name = "Applied name: {}"
    entered_actors = "Applied actors: {}"
    all_films = "No more movies according to your search criteria. Use /search_movies for new search."
    no_movies = "No movies according to your search criteria. Try to use another combination."
    select_genres = "Select genres:"
    selected_genre = "You selected the {} genre."
    selected_genres = "Applied genre(s): {}"
    selected_year_genres = "Applied:\nYear - {}\nGenres - {}"
    genres_selection_err = "You should select one or more genre. Please, select and submit again"
    show_next_n_movies = "Show next {} films?"
    dont_show_more_movies = """
I hope that you found something interesting to watch. 
If you wanna search more films - use my menu button or click on /search_movies"""
    welcome = """
Hi! I am a bot where you can search some movies using different search criteria. 
I have around 5k movies in my database.
By default just 10 films will be shown in the result. 
If you want to change it - use command <a>/set_default_amount</a>.
Type /help to check all available commands.
Enjoy it!"""
    parse_HTML = "HTML"
    mysql_err = "The error '{}' occurred"
    most_common_10_queries = "Most 10 common queries:\n"
    available_commands = """
/start - Start the bot
/set_default_amount - Change amount of movies for each search result. Default value - 10
/search_movies - Show different search criteria
/most_common_queries - Show 10 most popular search queries
/help - Show this help message     
    """


class Session:
    session = "session"
    amount = "default_film_amount"
    years = "years"
    year = "year"
    genres = "genres"
    amount_value = 10
    selected_genres = "selected_genres"
    current_page = "current_page"
    action = "action"
    keywords = "keywords"
    name = "name"
    actors = "actors"


class MenuCommands:
    set_default_amount = "set_default_amount"
    search_movies = "search_movies"
    most_common_queries = "most_common_queries"
    help = "help"


class MenuOptions:
    class Text:
        keywords = "Search by keywords"
        year = "Search by year"
        genres = "Search by genres"
        year_genres = "Search by year and genres"
        actors = "Search by actors"
        name = "Search by name"
        submit = "✅ Submit ✅"
        yes = "Yes"
        no = "No"

    class Meta:
        keywords = "search_by_keywords"
        search_year = "search_by_year"
        genres = "search_by_genres"
        year_genres = "search_by_year_genres"
        actors = "search_by_actors"
        name = "search_by_name"
        submit = "submit"
        yes = "next_films_yes"
        no = "next_films_no"
        year = "year_{}"
        genre = "genre_{}"
        yg_year = "ygyear_{}"
        yg_genre = "yggenre_{}"
        yg_submit = "ygsubmit"


class TableFields:
    id = "id"
    title = "title"
    year = "year"
    genres = "genres"
    plot = "plot"
    rating = "rating"
    poster = "poster"
    cast = "cast"
    directors = "directors"
    languages = "languages"
    type = "Type"
    field = "Field"


class MovieInfo:
    url = "{app_url}/movie?id={id}"
    caption = """
<b>Title:</b> {title}
<b>Rating:</b> IMDB - {rating}
<b>Description:</b>
{plot}
<a href='{url}'>More info...</a>
    """
    no_image_url = "https://nijomart.com/wp-content/uploads/2021/05/no_image.jpg"


class Environment:
    class Key:
        host = "host"
        user = "user"
        password = "password"
        database = "database"

    class Value:
        app_url = "app_url"
        telegram_token = "tg_token"
        host = "db_host"
        user = "db_user"
        password = "db_password"
        database = "db_name"
