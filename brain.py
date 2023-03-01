import asyncio
import logging
import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import openai


from config import TOKEN
from config import GDP

# Инициализируем API ключ от OpenAI
openai.api_key = GDP

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Friend", "Chat", "Marv", ""]
    keyboard.add(*buttons)
    await message.reply("Hi! I wanna kill u! {^,^} ", reply_markup=keyboard)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("No one can help u. I'll kill all u'r family {^,^}")


@dp.message_handler(commands=['del'])
async def process_start_command(message: types.Message):
    os.remove(f"dialog_{message.from_user.id}.txt")
    await message.answer("I kill u'r friend (* ^ ω ^)*")


@dp.message_handler(lambda message: message.text == "Friend")
async def with_puree(message: types.Message):
    with open('choices.json') as f:
        templates = json.load(f)
    templates[str(message.from_user.id)] = "FRIEND"
    with open('choices.json', 'w') as f:
        json.dump(templates, f)
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Chat")
async def with_puree(message: types.Message):
    with open('choices.json') as f:
        templates = json.load(f)
    templates[str(message.from_user.id)] = "CHAT"
    with open('choices.json', 'w') as f:
        json.dump(templates, f)
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Marv")
async def with_puree(message: types.Message):
    with open('choices.json') as f:
        templates = json.load(f)
    templates[str(message.from_user.id)] = "MARV"
    with open('choices.json', 'w') as f:
        json.dump(templates, f)
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler()
async def generate_text(message: types.Message):
    from_user = message.from_user.id
    with open('choices.json') as f:
        templates = json.load(f)
    with open('models.json') as f:
        models = json.load(f)

    if str(from_user) in templates:
        model_type = models[templates[str(from_user)]]
    else:
        await message.answer(f"Press start button and select the model")
        return

    save_dialog(message=f"Я: {message.text}", file_name=from_user)

    with open(f'dialog_{from_user}.txt', 'r') as file:
        prompt = file.read()

    try:
        completions = openai.Completion.create(
            model=model_type["model"],
            prompt=prompt + model_type["prompt"],
            max_tokens=model_type["max_tokens"],
            temperature=model_type["temperature"],
            top_p=model_type["top_p"],
            frequency_penalty=model_type["frequency_penalty"],
            presence_penalty=model_type["presence_penalty"],
            stop=model_type["stop"]
        )
    except Exception as err:
        st = str(err)
        start_ind = st.index("(")
        end_ind = st.index("in your prompt")
        count_of_tokens = 4000-int(st[start_ind+1:end_ind-1])
        if count_of_tokens > 0:
            completions = openai.Completion.create(
                model=model_type["model"],
                prompt=prompt + model_type["prompt"],
                max_tokens=count_of_tokens,
                temperature=model_type["temperature"],
                top_p=model_type["top_p"],
                frequency_penalty=model_type["frequency_penalty"],
                presence_penalty=model_type["presence_penalty"],
                stop=model_type["stop"]
            )
        else:
            await message.answer(f"Warning! Limit of tokens: {count_of_tokens}")
            return

    answer = completions.choices[0].text.replace("\n", "")

    if "Бот:" not in answer:
        save_dialog(message=f'Бот: {answer}', file_name=from_user)
    else:
        save_dialog(message=answer, file_name=from_user)

    message_text = answer.replace("Бот:", '')

    await message.answer(message_text)


def save_dialog(message, file_name):
    file_name = f"dialog_{file_name}.txt"
    with open(file_name, "a") as f:
        f.write(f'{message}\n')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
