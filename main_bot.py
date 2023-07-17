import datetime
import os
import lzma
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup,KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from get_data import check_user, insert_new_user, delete_user,\
    update_req, get_static_today, update_general_static, get_general_static, \
    get_static_week,get_static_month, allow_not_allow_processing, update_allow, update_not_allow
from config import TOKEN




bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()

class GetFile(StatesGroup):
    get_file = State()

class UserSecondCategory(StatesGroup):
    only_files = State()
class UserZeroCategory(StatesGroup):
    go_away = State()

@dp.message_handler(commands=['start'])
async def send_hello(message:Message):
    category = check_user(message.from_user.id)
    if category == 2:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb_1 = KeyboardButton('Загрузить файл для обработки')
        kb_2 = KeyboardButton('Выйти из раздела')
        kb.add(kb_1, kb_2)
        await message.answer('Здравствуйте, вы можете отправить файл для обработки.\n Чтобы выйти из раздела отправки файла, воспользуйтесь командой "Выйти из раздела"', reply_markup=kb)
        #await bot.send_message(5722062613,message.from_user.id)
        #await GetFile.get_file.set()
        await UserSecondCategory.only_files.set()
    elif category == 1:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton('Загрузить файл для обработки'), KeyboardButton('Добавить пользователя'))
        kb.add(KeyboardButton('Удалить пользователя'), KeyboardButton('Запретить обработку файлов'))
        kb.add(KeyboardButton('Разрешить обработку файлов'), KeyboardButton('Показать статистику'),
               KeyboardButton('Выйти из раздела'))

        await message.answer('Добро пожаловать. Вы обладаете правами суперпользователя!', reply_markup=kb)
    else:
        await message.answer('Вы не имеете доступ к сервису.')
        await UserZeroCategory.go_away.set()

class Not_Allow(StatesGroup):
    not_allow = State()

@dp.message_handler(text='Загрузить файл для обработки', state=UserSecondCategory.only_files)       #обработчик запроса для людей второй категории
async def get_file(message:Message, state:FSMContext):
    category = check_user(message.from_user.id)
    if category == 2:
        can_i_processing = allow_not_allow_processing()
        print('UserSecondCategory', can_i_processing)
        if not can_i_processing:
            await message.answer('Обработка документов запрещена')
            await state.finish()
            await Not_Allow.not_allow.set()
        else:
            await message.answer('Прикрепите документ')
            await state.finish()
            await GetFile.get_file.set()
    elif category == 0:
        await message.answer('Вас лишили права обрабатывать файлы.')
        await state.finish()
        await UserZeroCategory.go_away.state()

@dp.message_handler(content_types=['any'], state=Not_Allow.not_allow)
async def not_allow(message:Message, state:FSMContext):
    can_i_processing = allow_not_allow_processing()
    if not can_i_processing:
        await message.delete()
    elif can_i_processing:
        await message.answer('Обработка документов разрешена \n Повторите, пожалуйста, команду снова.')
        await state.finish()
        await UserSecondCategory.only_files.set()

@dp.message_handler(state=UserSecondCategory.only_files)
async def answer_to_user_2(message:Message, state:FSMContext):
    category = check_user(message.from_user.id)
    if category == 0:
        await message.answer('Вас лишили доступа к сервису.')
        await state.finish()
        await UserZeroCategory.go_away.set()
    elif category == 2:
        r = allow_not_allow_processing()
        if not r:
            await message.answer('Обработка файлов запрещена.')
            await state.finish()
            await Not_Allow.not_allow.state()
        else:
            await message.reply('Вам доступна отправка файлов.')
    #await message.answer('Режим обработки файлов выключен')

@dp.message_handler(state=UserZeroCategory.go_away)
async def go_away(message:Message, state:FSMContext):
    category = check_user(message.from_user.id)

    if category == 2:
        await message.answer('Вам стала доступной обработка файлов. Пришлите ваше сообщение, пожалуйста, снова.')
        await state.finish()
        await UserSecondCategory.only_files.set()
    if category == 1:
        await message.answer('Теперь вы обладаете правами суперпользователя!')
        await state.finish()
    elif category == 0:
        await message.reply('Вы не имеете доступ к сервису.')

@dp.message_handler(commands=['help'])
async def send_help(message:Message):
    await message.reply()



@dp.message_handler(text='Загрузить файл для обработки')                #обработчик для первой категории и тех, кто раньше был первой категорией
async def get_file(message:Message):
    category = check_user(message.from_user.id)
    answer = allow_not_allow_processing()
    if category == 1:
        await message.answer('Прикрепите документ')
        await GetFile.get_file.set()
    if not answer:
        await message.answer('Обработка документов запрещена')
    else:
        if category == 0:
            await message.answer('Вас лишили возможности обрабатывать файлы.')
            await UserZeroCategory.go_away.set()
        elif category == 2:
            await message.answer('Прикрепите документ')
            await GetFile.get_file.set()


@dp.message_handler(content_types=['text','document'], state=GetFile.get_file)          #обработка файлов для пользователей 1 и 2 категории
async def get_file(message:Message, state:FSMContext):
    category = check_user(message.from_user.id)
    if category == 0:
        await state.finish()
        await message.answer('Вас лишили возможности обрабатывать файлы.')
        await UserZeroCategory.go_away.state()
    elif message.text =='Загрузить файл для обработки':
        await message.answer('Прикрепите документ')
        return
    try:
        if message.text == 'Выйти из раздела':
            if category == 1:
                await message.answer('Вы вышли из раздела')
                await state.finish()
            elif category == 2:
                await message.answer('Вы вышли из раздела')
                await state.finish()
                await UserSecondCategory.only_files.set()
        elif message.document['mime_type'] == 'text/plain':
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("_%Y-%m-%d_%H-%M-%S")
            print(formatted_datetime)
            file = await bot.get_file(message.document.file_id)
            file_name = message.document.file_name
            file_name = file_name.split('.')[0]
            file_path = file.file_path
            file_name_date =str(formatted_datetime)
            way = f'\Tg-bots\Telegram_bots\pythonProject\pythonProject3\cin\{file_name + file_name_date}'
            await bot.download_file(file_path,way)
            await message.answer('Файл принят в обработку')
            update_req(message.from_user.id)
            update_general_static(message.from_user.id)
            #===============================================================
            def compress_file(input_file, output_file):
                with open(input_file, 'rb') as f_in, lzma.open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())

            # Пример использования
            input_file = way  # Путь к входному файлу
            output_file = f'\Tg-bots\Telegram_bots\pythonProject\pythonProject3\cout\{file_name + file_name_date}.xz'  # Путь к сжатому файлу

            compress_file(input_file, output_file)
            #===============================================================
            path_xz = f'\Tg-bots\Telegram_bots\pythonProject\pythonProject3\cout\{file_name + file_name_date}.xz'
            await bot.send_document(message.from_user.id, document=open(path_xz, 'rb'))
            if category == 1:
                await state.finish()
            if category == 2:
                await state.finish()
                await UserSecondCategory.only_files.set()
        else:
            await message.answer('Некорректный формат файла. Отправьте, пожалуйста, файл в формате txt.')
    except:
        await message.answer('Некорректный формат файла. Отправьте, пожалуйста, файл в формате txt.')

@dp.message_handler(text='Показать статистику')
async def show_statistic(message:Message):
    category = check_user(message.from_user.id)
    if category == 1:
        m = InlineKeyboardMarkup()
        lst = ['По каждому пользователю','За сегодня', 'За неделю', 'За месяц']
        for i in range(4):
            m.insert(InlineKeyboardButton(text=lst[i], callback_data=f'date{lst[i]}'))
        path = r'E:\Tg-bots\Telegram_bots\pythonProject\pythonProject3\data.csv'
        await message.answer('Статистика какого вида вам нужна?', reply_markup=m)
    else:
        await message.answer('Вы больше не обладаете правами суперпользователя!')
        await UserZeroCategory.go_away.set()

@dp.callback_query_handler(text_startswith='date')
async def static_choice(call:CallbackQuery):
    choice = call.data[4:]
    if choice == 'По каждому пользователю':
        await call.answer()
        result = get_general_static()
        if result != False:
            await bot.send_message(call.from_user.id, text='Статистика по каждому пользователю')
            path = r'E:\Tg-bots\Telegram_bots\pythonProject\pythonProject3\data.csv'
            await bot.send_document(call.from_user.id, document=open(path, 'rb'))
            if os.path.isfile(path):
                os.remove(path)
                return
        else:
            await bot.send_message(call.from_user.id, text = 'Таблица пуста')
            return

    elif choice == 'За сегодня':
        await call.answer()
        result = get_static_today()
        if result == False:
            await bot.send_message(call.from_user.id, text='На сегодняшний день записей не найдено')
            return
        else:
            await bot.send_message(call.from_user.id, text='Статистика за сегодняшний день')
            path = r'E:\Tg-bots\Telegram_bots\pythonProject\pythonProject3\data.csv'
            await bot.send_document(call.from_user.id, document=open(path, 'rb'))
            if os.path.isfile(path):
                os.remove(path)

    elif choice == 'За неделю':
        await call.answer()
        result = get_static_week()
        if result != False:
            await bot.send_message(call.from_user.id, text='Статистика за последнюю неделю')
            path = r'E:\Tg-bots\Telegram_bots\pythonProject\pythonProject3\data.csv'
            await bot.send_document(call.from_user.id, document=open(path, 'rb'))
            if os.path.isfile(path):
                os.remove(path)

        else:
            await bot.send_message(call.from_user.id, text='Записей последнюю неделю не найдено')
    elif choice == 'За месяц':
        await call.answer()
        result = get_static_month()
        if result != False:
            await bot.send_message(call.from_user.id, text='Статистика за последний месяц')
            path = r'E:\Tg-bots\Telegram_bots\pythonProject\pythonProject3\data.csv'
            await bot.send_document(call.from_user.id, document=open(path, 'rb'))
            if os.path.isfile(path):
                os.remove(path)

        else:
            await bot.send_message(call.from_user.id, text='Записей последний месяц не найдено')

#'Запретить обработку файлов' 'Разрешить обработку файлов'

@dp.message_handler(text='Запретить обработку файлов')
async def not_processing_command(message:Message):
    category = check_user(message.from_user.id)
    if category == 1:
        update_not_allow(message.from_user.id)
        await message.answer('Обработка файлов запрещена')
    else:
        await message.answer('Вы больше не обладаете правами суперпользователя!')
        await UserZeroCategory.go_away.set()

@dp.message_handler(text='Разрешить обработку файлов')
async def not_processing_command(message:Message):
    category = check_user(message.from_user.id)
    if category == 1:
        update_allow(message.from_user.id)
        await message.answer('Обработка файлов разрешена')
    else:
        await message.answer('Вы больше не обладаете правами суперпользователя!')
        await UserZeroCategory.go_away.set()


@dp.message_handler(text='Добавить пользователя')
async def write_user(message: Message):
    category = check_user(message.from_user.id)
    if category == 1:
        markup = InlineKeyboardMarkup(row_width=1)
        answers = ['У меня есть user_id','У меня нет user_id']
        for i in answers:
            markup.insert(InlineKeyboardButton(i, callback_data=f'id{i}'))
        await message.answer('Какая у вас ситуация?', reply_markup=markup)
    else:
        await message.answer('Вы больше не обладаете правами суперпользователя!')
        await UserZeroCategory.go_away.set()

class GetUserId(StatesGroup):
    user_id = State()

class GetForwardMessage(StatesGroup):
    forward = State()




@dp.callback_query_handler(text_startswith='id')
async def user_id(call:CallbackQuery):
    answ = call.data[2:]
    if answ == 'У меня есть user_id':
        await bot.send_message(call.from_user.id, 'Пожалуйста, пришлите его в чат.')
        await GetUserId.user_id.set()
    else:
        await bot.send_message(call.from_user.id, 'Пожалуйста, перешлите в данный чат сообщение от того пользователя, которого нужно добавить.')
        await GetForwardMessage.forward.set()
    await call.answer()


@dp.message_handler(state=GetForwardMessage.forward)
async def send_message(message: Message, state: FSMContext):
    try:
        if message.text == 'Выйти из раздела':
            await state.finish()
            await message.answer('Вы вышли из раздела.')
            return
        async with state.proxy() as data:
            data['user_id'] = message.forward_from.id
            bl = insert_new_user(data['user_id'])
            if bl:
                await message.answer('Пользователь успешно добавлен.')
                await state.finish()
            else:
                await message.answer('Пользователь уже есть в базе данных.')
                await state.finish()
    except:
        await message.reply(
            'Пожалуйста, перешлите в данный чат сообщение от того пользователя, которого нужно добавить.')


@dp.message_handler(state=GetUserId.user_id)
async def send_message(message: Message, state: FSMContext):
    if message.text == 'Выйти из раздела':
        await state.finish()
        await message.answer('Вы вышли из раздела.')
        return
    if 4 < len(message.text) < 11:
        async with state.proxy() as data:
            data['user_id'] = int(message.text)
            bl = insert_new_user(data['user_id'])
            if bl:
                await message.answer('Пользователь успешно добавлен.')
                await state.finish()
            else:
                await message.answer('Пользователь уже есть в базе данных.')
                await state.finish()
    else:
        await message.reply('Некорректные данные. Введите, пожлуйста, user_id снова.')


@dp.message_handler(text='Удалить пользователя')
async def del_user(message:Message):
    category = check_user(message.from_user.id)
    if category == 1:
        markup = InlineKeyboardMarkup(row_width=1)
        answers = ['У меня есть user_id', 'У меня нет user_id']
        for i in answers:
            markup.insert(InlineKeyboardButton(i, callback_data=f'del{i}'))
        await message.answer('Какая у вас ситуация?', reply_markup=markup)
    else:
        await message.answer('Вы больше не обладаете правами суперпользователя!')
        await UserZeroCategory.go_away.set()
class DelUserID(StatesGroup):
    delite_id = State()

class DelFromForwardId(StatesGroup):
    delite_forward = State()
@dp.callback_query_handler(text_startswith='del')
async def d_user(call:CallbackQuery):
    answ = call.data[3:]
    if answ == 'У меня есть user_id':
        await bot.send_message(call.from_user.id, 'Пожалуйста, пришлите его в чат.')
        await DelUserID.delite_id.set()
    else:
        await bot.send_message(call.from_user.id, 'Пожалуйста, перешлите в данный чат сообщение от того пользователя, которого нужно добавить.')
        await DelFromForwardId.delite_forward.set()
    await call.answer()

@dp.message_handler(state=DelUserID.delite_id)
async def del_user_id(message:Message, state:FSMContext):
    try:
        if message.text == 'Выйти из раздела':
            await state.finish()
            await message.answer('Вы вышли из раздела.')
            return
        if 4 < len(message.text) < 15:
            async with state.proxy() as data:
                data['user_id'] = int(message.text)
                bl = delete_user(data['user_id'])
                if bl:
                    await message.answer('Пользователь успешно удален.')
                    await state.finish()
                else:
                    await message.answer('Запись о пользователе отсутствует.')
                    await state.finish()
        else:
            await message.reply('Некорректные данные. Введите, пожлуйста, user_id снова.')
    except:
        await message.reply('Некорректные данные. Введите, пожлуйста, user_id снова.')

@dp.message_handler(state=DelFromForwardId)
async def send_message(message:Message, state:FSMContext):
    try:
        if message.text == 'Выйти из раздела':
            await state.finish()
            await message.answer('Вы вышли из раздела.')
            return
        async with state.proxy() as data:
            data['user_id'] = message.forward_from.id
            bl = delete_user(data['user_id'])
            if bl:
                await message.answer('Пользователь успешно удален.')
                await state.finish()
            else:
                await message.answer('Запись о пользователе отсутствует.')
                await state.finish()
    except:
        await message.reply('Пожалуйста, перешлите в данный чат сообщение от того пользователя, которого нужно удалить из базы данных.')





if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)