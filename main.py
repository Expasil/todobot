from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import db
API_TOKEN = ''


Storage=MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=Storage)



class NewTask(StatesGroup):
    name=State()


async def on_startup(_):
    await db.db_start()
    print('Бот успешно запущен')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')



main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Добавить задачу').add('Отметить выполненной').add('Все задачи').add('Удалить задачу')

#Запуск бота
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f'{message.from_user.first_name}, добро пожаловать в бот управления списком задач',reply_markup=main)

#Добавляем задачу
@dp.message_handler(text='Добавить задачу')
async def add_task(message: types.Message):
    await NewTask.name.set()
    await message.answer(f'Введите название задачи', reply_markup=cancel)


@dp.message_handler(state=NewTask.name)
async def add_task_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = None
        data['task_text'] = None   
    if message.text != 'Отмена':
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['task_text'] = message.text
        await db.add_task_to_db(state)
        await message.answer('Задание создано', reply_markup=main)
    else:
        await message.answer('Добавление задачи отменено.', reply_markup=main)
    await state.finish()

#Выводим все задачи
@dp.message_handler(text='Все задачи')
async def get_all_tasks(message: types.Message):
    tasklist = await db.get_users_task_from_db(message.from_user.id)    
    result = ''
    for task in tasklist:
        # Assuming the name of the task is in the second column (index 1)
        
        # Create the InlineKeyboardButton and append it to the buttons list
        if task[3]>0:
            result+=(task[2]+' ✓'+"\n")
        else:
            result+=(task[2]+"\n")
    if result == '':
        await message.answer('У вас нет поставленных задач', reply_markup=main)
    else:
        await message.answer('Ваши задачи:'+'\n'+result, reply_markup=main)



#Удаляем выбранную задачу
@dp.message_handler(text='Удалить задачу')
async def delete_task(message: types.Message):
    tasklist = await db.get_users_task_from_db(message.from_user.id)
    buttons = []
    # print(tasklist)
    if tasklist == []:
        await message.answer('У вас нет поставленных задач', reply_markup=main)
    else:
        for task in tasklist:
            if task[3]>0:
                buttons.append(InlineKeyboardButton(task[2]+' ✓', callback_data=f"delete_task:{task[0]}"))
            else:
                buttons.append(InlineKeyboardButton(task[2], callback_data=f"delete_task:{task[0]}"))
        tasks = InlineKeyboardMarkup(row_width=1)
        tasks.add(*buttons)
        await message.answer('Ваши задачи:', reply_markup=tasks)


@dp.callback_query_handler(lambda c: c.data.startswith('delete_task:'))
async def delete_task_callback(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split(":")[1]
    await db.delete_users_task_from_db(callback_query.from_user.id, task_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text='Задача удалена')



#Отмечаем задачу выполненной
@dp.message_handler(text='Отметить выполненной')
async def get_task_done(message: types.Message):
    tasklist = await db.get_undone_users_task_from_db(message.from_user.id)
    buttons = []
    if tasklist == []:
        await message.answer('У вас нет поставленных задач', reply_markup=main)
    else:
        for task in tasklist:
            buttons.append(InlineKeyboardButton(task[2], callback_data=f"update_task:{task[0]}"))
        tasks = InlineKeyboardMarkup(row_width=1)
        tasks.add(*buttons)
        await message.answer('Ваши задачи:', reply_markup=tasks)


@dp.callback_query_handler(lambda c: c.data.startswith('update_task:'))
async def update_task_callback(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split(":")[1]
    await db.update_users_task_in_db(callback_query.from_user.id,task_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text='Задача обновлена')



@dp.message_handler()
async def start(message: types.Message):
    await message.answer('Я тебя не понимаю',reply_markup=main)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,on_startup=on_startup)