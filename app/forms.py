from aiogram.fsm.state import State, StatesGroup


class DefaultAmountForm(StatesGroup):
    amount = State()


class KeywordsForm(StatesGroup):
    keywords = State()


class NameForm(StatesGroup):
    name = State()


class ActorsForm(StatesGroup):
    actors = State()
