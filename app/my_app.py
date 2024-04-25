from aiogram.fsm.context import FSMContext
from os import getenv
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)

from app.forms import DefaultAmountForm, KeywordsForm, NameForm, ActorsForm
from app.constants import (
    Messages as Msg,
    Session as Ses,
    MenuCommands as Com,
    MenuOptions as Opt,
    TableFields as Tf,
    Environment as Env,
    MovieInfo as Mi
)
from service import AppService


class MyApp:
    def __init__(self, token):
        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=MemoryStorage())
        self.service = AppService()
        self.register_handlers()

    def register_handlers(self):
        @self.dp.message(CommandStart())
        async def command_start_handler(message: Message, state: FSMContext):
            await self.dp.storage.set_data(Ses.session, {Ses.amount: Ses.amount_value})
            await self.dp.storage.update_data(Ses.session, {Ses.years: self.service.get_all_production_years()})
            await self.dp.storage.update_data(Ses.session, {Ses.genres: self.service.get_all_genres()})

            await message.answer(Msg.welcome, parse_mode=Msg.parse_HTML)
            await command_search_movies_handler(message, state)

        @self.dp.message(Command(Com.most_common_queries))
        async def command_most_common_queries_handler(message: Message):
            result_dict = self.service.show_most_common_queries()
            queries = [f"{index + 1}. Search query: '{dictionary['query']}'. Repeats: {dictionary['query_count']}" for
                       index, dictionary in enumerate(result_dict)]
            await message.answer(Msg.most_common_10_queries + "\n".join(queries))

        @self.dp.message(Command(Com.help))
        async def command_help_handler(message: Message):
            await message.answer(Msg.available_commands)

        @self.dp.message(Command(Com.search_movies))
        async def command_search_movies_handler(message: Message, state: FSMContext):
            await state.clear()
            keyboards = [
                [InlineKeyboardButton(text=Opt.Text.keywords, callback_data=Opt.Meta.keywords)],
                [InlineKeyboardButton(text=Opt.Text.name, callback_data=Opt.Meta.name)],
                [InlineKeyboardButton(text=Opt.Text.year, callback_data=Opt.Meta.search_year)],
                [InlineKeyboardButton(text=Opt.Text.genres, callback_data=Opt.Meta.genres)],
                [InlineKeyboardButton(text=Opt.Text.year_genres, callback_data=Opt.Meta.year_genres)],
                [InlineKeyboardButton(text=Opt.Text.actors, callback_data=Opt.Meta.actors)]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)
            await message.answer(Msg.select_option, reply_markup=keyboard)

        # START: Set amount functionality
        @self.dp.message(Command(Com.set_default_amount))
        async def command_set_default_amount_handler(message: Message, state: FSMContext):
            await state.set_state(DefaultAmountForm.amount)
            await message.answer(Msg.enter_new_amount, reply_markup=ReplyKeyboardRemove())

        @self.dp.message(DefaultAmountForm.amount)
        async def process_amount(message: Message, state: FSMContext):
            if not message.text.isdigit() or message.text == "0":
                await message.answer(Msg.digits_invalid)
                return await command_set_default_amount_handler(message, state)

            await self.dp.storage.update_data(Ses.session, {Ses.amount: int(message.text)})
            await message.answer(Msg.success_new_amount.format(message.text))
            await state.clear()

        # END: Set amount functionality

        # START: Search by keywords functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.keywords)
        async def process_keywords_callback_button(callback_object: types.CallbackQuery | types.Message,
                                                   state: FSMContext):
            await state.set_state(KeywordsForm.keywords)
            call_obj = get_object_for_answer(callback_object)
            await call_obj.answer(Msg.enter_keywords, reply_markup=ReplyKeyboardRemove())

        @self.dp.message(KeywordsForm.keywords)
        async def process_keywords(message: Message, state: FSMContext):
            state_data = await state.get_data()
            if not state_data.get(Ses.action):
                keywords = message.text
                if not all(char.isalnum() or char.isspace() for char in keywords):
                    await message.answer(Msg.keywords_invalid)
                    return await process_keywords_callback_button(message, state)

                self.service.save_query(f"{Ses.keywords}: {keywords}", message.from_user.id)
                await state.update_data(action=Opt.Meta.keywords, keywords=keywords)
            else:
                keywords = state_data.get(Ses.keywords)

            await message.answer(text=Msg.entered_keywords.format(keywords))

            current_page = await get_current_page(state)
            amount = await get_amount()
            films = self.service.get_films_by_keywords(keywords, amount, current_page)

            if len(films) == 0:
                return await try_again_if_0_films(message, state, process_keywords_callback_button)

            await show_films(films, message)
            await show_next_films(films, message, state)

        # END: Search by keywords functionality

        # START: Search by name functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.name)
        async def process_name_callback_button(callback_object: types.CallbackQuery | types.Message,
                                               state: FSMContext):
            await state.set_state(NameForm.name)
            call_obj = get_object_for_answer(callback_object)
            await call_obj.answer(Msg.enter_name, reply_markup=ReplyKeyboardRemove())

        @self.dp.message(NameForm.name)
        async def process_name(message: Message, state: FSMContext):
            state_data = await state.get_data()
            if not state_data.get(Ses.action):
                name = message.text
                self.service.save_query(f"{Ses.name}: {name}", message.from_user.id)
                await state.update_data(action=Opt.Meta.name, name=name)
            else:
                name = state_data.get(Ses.name)

            await message.answer(text=Msg.entered_name.format(name))

            current_page = await get_current_page(state)
            amount = await get_amount()
            films = self.service.get_films_by_name(name, amount, current_page)

            if len(films) == 0:
                return await try_again_if_0_films(message, state, process_name_callback_button)

            await show_films(films, message)
            await show_next_films(films, message, state)

        # END: Search by name functionality

        # START: Search by year functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.search_year)
        async def process_years_callback_button(callback_query: types.CallbackQuery, data_format=Opt.Meta.year):
            data = await self.dp.storage.get_data(Ses.session)
            years = data.get(Ses.years)
            keyboards = [[]]
            it = 0
            for index, year in enumerate(years):
                keyboards[it].append(InlineKeyboardButton(text=year, callback_data=data_format.format(year)))
                if (index + 1) % 5 == 0 and (index + 1) < len(years):
                    it += 1
                    keyboards.append([])
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

            await callback_query.message.answer(Msg.select_year, reply_markup=keyboard)

        @self.dp.callback_query(lambda c: c.data.startswith(Opt.Meta.year.format("")))
        async def process_concrete_year_selection(callback_query: types.CallbackQuery, state: FSMContext):
            state_data = await state.get_data()

            if not state_data.get(Ses.action):
                year = callback_query.data.split('_')[1]
                self.service.save_query(f"{Ses.year}: {year}", callback_query.from_user.id)
                await state.update_data(action=Opt.Meta.year.format(year))
            else:
                year = state_data.get(Ses.action).split('_')[1]

            await callback_query.message.answer(text=Msg.selected_year.format(year))

            current_page = await get_current_page(state)
            amount = await get_amount()
            films = self.service.get_films_by_year(year, amount, current_page)

            await show_films(films, callback_query)
            await show_next_films(films, callback_query, state)

        # END: Search by year functionality

        # START: Search by genres functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.genres)
        async def process_genres_callback_button(callback_query: types.CallbackQuery, data_format=Opt.Meta.genre,
                                                 submit_btn=Opt.Meta.submit):
            data = await self.dp.storage.get_data(Ses.session)
            genres = data.get(Ses.genres)
            buttons = [InlineKeyboardButton(text=genre, callback_data=data_format.format(genre)) for genre in genres]
            keyboards = ([buttons[i:i + 2] for i in range(0, len(buttons), 2)] +
                         [[InlineKeyboardButton(text=Opt.Text.submit, callback_data=submit_btn)]])

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

            await callback_query.message.answer(Msg.select_genres, reply_markup=keyboard)

        @self.dp.callback_query(
            lambda c: c.data.startswith(Opt.Meta.genre.format("")) or c.data.startswith(Opt.Meta.yg_genre.format("")))
        async def process_genre_selection(callback_query: types.CallbackQuery, state: FSMContext):
            selected_genre = callback_query.data.split('_')[1]
            data = await state.get_data()
            sel_genres = data.get(Ses.selected_genres, [])
            sel_genres.append(selected_genre)
            await state.update_data(selected_genres=sel_genres)
            await callback_query.answer(text=Msg.selected_genre.format(selected_genre))

        @self.dp.callback_query(lambda c: c.data in (Opt.Meta.submit, Opt.Meta.yg_submit))
        async def process_submit_button(callback_query: types.CallbackQuery, state: FSMContext):
            data = await state.get_data()
            selected_genres = await selected_genres_validation(callback_query, data)

            current_page = await get_current_page(state)
            amount = await get_amount()
            genres = ', '.join(selected_genres)

            if not data.get(Ses.action):
                action = callback_query.data
                year = data.get(Ses.year)
                message = f"{Ses.genres}: {genres}{f'; {Ses.year}: {year}' if year else ''}"
                self.service.save_query(message, callback_query.from_user.id)
                await state.update_data(action=action)
            else:
                action = data.get(Ses.action)

            if action == Opt.Meta.submit:
                await callback_query.message.answer(text=Msg.selected_genres.format(genres))
                films = self.service.get_films_by_genres(selected_genres, amount, current_page)
            else:
                year = data.get(Ses.year)
                await callback_query.message.answer(text=Msg.selected_year_genres.format(year, genres))
                films = self.service.get_films_by_year_n_genres(year, selected_genres, amount, current_page)

            if len(films) == 0:
                f = process_genres_callback_button if action == Opt.Meta.submit else process_year_genres_callback_button
                return await try_again_if_0_films(callback_query, state, f)

            await show_films(films, callback_query)
            await show_next_films(films, callback_query, state)

        # END: Search by genres functionality

        # START: Search by year and genres functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.year_genres)
        async def process_year_genres_callback_button(callback_query: types.CallbackQuery):
            await process_years_callback_button(callback_query, data_format=Opt.Meta.yg_year)

        @self.dp.callback_query(lambda c: c.data.startswith(Opt.Meta.yg_year.format("")))
        async def process_yg_year_selection(callback_query: types.CallbackQuery, state: FSMContext):
            year = callback_query.data.split("_")[1]
            await state.update_data(year=year)
            await process_genres_callback_button(callback_query, data_format=Opt.Meta.yg_genre,
                                                 submit_btn=Opt.Meta.yg_submit)

        # END: Search by year and genres functionality

        # START: Search by actors functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.actors)
        async def process_actors_callback_button(callback_object: types.CallbackQuery | types.Message,
                                                 state: FSMContext):
            await state.set_state(ActorsForm.actors)
            call_obj = get_object_for_answer(callback_object)
            await call_obj.answer(Msg.enter_actors, reply_markup=ReplyKeyboardRemove())

        @self.dp.message(ActorsForm.actors)
        async def process_actors(message: Message, state: FSMContext):
            state_data = await state.get_data()
            if not state_data.get(Ses.action):
                actors = sort_format_actors(message.text.split(","))
                self.service.save_query(f"{Ses.actors}: {', '.join(actors)}", message.from_user.id)
                await state.update_data(action=Opt.Meta.actors, actors=actors)
            else:
                actors = state_data.get(Ses.actors)

            await message.answer(text=Msg.entered_actors.format(", ".join(actors)))

            current_page = await get_current_page(state)
            amount = await get_amount()
            films = self.service.get_films_by_actors(actors, amount, current_page)
            if len(films) == 0:
                return await try_again_if_0_films(message, state, process_actors_callback_button)

            await show_films(films, message)
            await show_next_films(films, message, state)

        # END: Search by actors functionality

        # START: Pagination functionality
        @self.dp.callback_query(lambda c: c.data == Opt.Meta.yes)
        async def process_next_films_yes_button(callback_query: types.CallbackQuery, state: FSMContext):
            current_page = await get_current_page(state)
            await state.update_data(current_page=(current_page + 1))
            data = await state.get_data()
            action = data.get(Ses.action)

            if action is None:
                return await unknown_command_handler(callback_query.message, state)

            if action in (Opt.Meta.submit, Opt.Meta.yg_submit):
                await process_submit_button(callback_query, state)
            elif action.startswith(Opt.Meta.year.format("")):
                await process_concrete_year_selection(callback_query, state)
            elif action == Opt.Meta.keywords:
                await process_keywords(callback_query.message, state)
            elif action == Opt.Meta.name:
                await process_name(callback_query.message, state)
            elif action == Opt.Meta.actors:
                await process_actors(callback_query.message, state)

        @self.dp.callback_query(lambda c: c.data == Opt.Meta.no)
        async def process_next_films_no_button(callback_query: types.CallbackQuery, state: FSMContext):
            await state.clear()
            await callback_query.message.answer(Msg.dont_show_more_movies)

        async def next_films(callback_object: types.CallbackQuery | types.Message):
            amount = await get_amount()

            keyboards = [
                [InlineKeyboardButton(text=Opt.Text.yes, callback_data=Opt.Meta.yes),
                 InlineKeyboardButton(text=Opt.Text.no, callback_data=Opt.Meta.no)]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

            call_obj = get_object_for_answer(callback_object)
            await call_obj.answer(Msg.show_next_n_movies.format(amount), reply_markup=keyboard)

        async def show_next_films(films, callback_object: types.CallbackQuery | types.Message, state: FSMContext):
            amount = await get_amount()
            call_obj = get_object_for_answer(callback_object)
            if len(films) < amount:
                await call_obj.answer(text=Msg.all_films)
                await state.clear()
            else:
                await next_films(callback_object)

        # END: Pagination functionality

        # START: Help methods

        def get_object_for_answer(callback_object: types.CallbackQuery | types.Message):
            return callback_object.message if isinstance(callback_object, types.CallbackQuery) else callback_object

        async def send_movie_info(callback_query: types.CallbackQuery | types.Message, film):
            url = Mi.url.format(app_url=getenv(Env.Value.app_url), id=film[Tf.id])
            caption = Mi.caption.format(title=film[Tf.title], rating=film[Tf.rating], plot=film[Tf.plot], url=url)
            chat_id = callback_query.from_user.id if isinstance(callback_query,
                                                                types.CallbackQuery) else callback_query.chat.id
            photo_url = check_photo_url(film[Tf.poster])
            await self.bot.send_photo(chat_id=chat_id,
                                      photo=photo_url,
                                      caption=caption,
                                      parse_mode=Msg.parse_HTML)

        async def show_films(films, callback_object: types.CallbackQuery | types.Message):
            for film in films:
                await send_movie_info(callback_object, film)

        def check_photo_url(photo_url):
            result = requests.get(photo_url)
            if result.status_code != 200:
                return Mi.no_image_url
            return photo_url

        async def get_current_page(state: FSMContext):
            data = await state.get_data()
            current_page = data.get(Ses.current_page)
            if not current_page:
                current_page = 1
                await state.update_data(current_page=current_page)
            return int(current_page)

        async def get_amount():
            session_data = await self.dp.storage.get_data(Ses.session)
            return session_data.get(Ses.amount)

        async def selected_genres_validation(callback_query: types.CallbackQuery, data):
            selected_genres = data.get(Ses.selected_genres, [])
            if len(selected_genres) == 0:
                return await callback_query.message.answer(text=Msg.genres_selection_err)
            return sorted(selected_genres)

        def sort_format_actors(actors):
            return sorted([" ".join(a.split()) for a in actors])

        async def try_again_if_0_films(callback_object: types.CallbackQuery | types.Message, state: FSMContext,
                                       func):
            call_obj = get_object_for_answer(callback_object)
            await call_obj.answer(text=Msg.no_movies)
            await state.clear()
            return await func(callback_object, state)

        # END: Help methods

        @self.dp.message()
        async def unknown_command_handler(message: Message, state: FSMContext) -> None:
            await message.answer(Msg.unknown_command)
            await state.clear()
            await command_search_movies_handler(message, state)
