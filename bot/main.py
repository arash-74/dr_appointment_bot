from jdatetime import datetime
from decouple import config
import aiohttp
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton

list_user_appointment = []
list_appointment = []


def method_finder(target_method):
    methods = {
        'welcome_handler': welcome_handler,
        'list_book_appointment': list_book_appointment,
        'appointment_handler': appointment_handler,
        'remove_appointment_handler': remove_appointment_handler,
        'list_available_appointment': list_available_appointment,
        'appointment_detail_available_handler': appointment_detail_available_handler,
        'appointment_book': appointment_book
    }
    return methods.get(target_method)


async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8000/api/create-user/', json={"chat_id": chat_id}) as response:
                if response.status != 200:
                    await update.message.reply_text('خطایی در شبکه رخ داده است مجدد تلاش کنید')
    except aiohttp.client_exceptions.ClientConnectorError:
        await update.message.reply_text('خطایی در شبکه رخ داده است مجدد تلاش کنید')
    else:
        text = "سلام 👋\nبه ربات نوبت دهی آنلاین دکتر آرش خوش آمدید\nلطفا یک مورد را انتخاب کنید👇"
        keyboards = [
            [InlineKeyboardButton('گرفتن نوبت', callback_data='list_available_appointment')],
            [InlineKeyboardButton('لیست نوبت های گرفته شده', callback_data='list_book_appointment')],
        ]
        keyboard_markup = InlineKeyboardMarkup(keyboards)
        if update.callback_query:
            await context.bot.edit_message_text(text, reply_markup=keyboard_markup, chat_id=chat_id,
                                                message_id=message_id)
        else:
            await context.bot.send_message(text=text, reply_markup=keyboard_markup, chat_id=chat_id)


async def keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    message_id = update.effective_message.id
    keyboard = [[InlineKeyboardButton('تلاش مجدد', callback_data='welcome_handler')]]
    await query.answer()
    if len(query.data.split('-')) > 1:
        target_method = query.data.split('-')[0]
        await method_finder(target_method)(update, context, data=query.data.split('-')[1])
    else:
        await method_finder(query.data)(update, context)
    # except TypeError:
    #     await context.bot.edit_message_text(text='خطایی رخ داده است مجدد تلاش کنید', chat_id=update.effective_chat.id,
    #                                         message_id=message_id, reply_markup=InlineKeyboardMarkup(keyboard))


async def list_available_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    global list_appointment
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://localhost:8000/api/appointment/list/only_unbook') as response:
            list_appointment = await response.json()

    appointment_keyboards = [
        InlineKeyboardButton(f"{appoint['from_date'][:10]} {appoint['from_date'][11:16]}",
                             callback_data=f'appointment_detail_available_handler-{list_appointment.index(appoint)}')
        for appoint in
        list_appointment]
    keyboards = [appointment_keyboards, [InlineKeyboardButton('بازگشت', callback_data='welcome_handler')]]
    keyboard_markup = InlineKeyboardMarkup(keyboards)
    text = f'نوبت های موجود ({len(list_appointment)})'
    await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=keyboard_markup)


async def appointment_detail_available_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    global list_appointment
    appointment = list_appointment[int(data)]
    text = f"تارخ نوبت:\n {appointment['from_date'][:10]} {appointment['from_date'][11:16]}"
    keyboards = [[InlineKeyboardButton('پرداخت', callback_data=f'appointment_book-{data}')],
                 [InlineKeyboardButton('بازگشت', callback_data='list_available_appointment')]]
    keyboard_markup = InlineKeyboardMarkup(keyboards)
    await context.bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard_markup)


async def appointment_book(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    global list_appointment
    appointment = list_appointment[int(data)]
    async with aiohttp.ClientSession() as session:
        async with session.put(f'http://localhost:8000/api/appointment/booking/{appointment['id']}',
                               json={"chat_id": chat_id}) as response:
            if response.status == 200:
                await success_payment_handler(update,context)


async def list_book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    global list_user_appointment
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://localhost:8000/api/appointment/user-booking/{chat_id}') as response:
                list_user_appointment = await response.json()
                # if response.status != 200:
                #     await update.message.reply_text('خطایی در شبکه رخ داده است مجدد تلاش کنید')
    except aiohttp.client_exceptions.ClientConnectorError:
        await update.message.reply_text('خطایی در شبکه رخ داده است مجدد تلاش کنید')
    appointment_keyboards = [
        InlineKeyboardButton(f"{appoint['from_date'][:10]} {appoint['from_date'][11:16]}",
                             callback_data=f'appointment_handler-{list_user_appointment.index(appoint)}')
        for appoint in
        list_user_appointment]
    keyboards = [appointment_keyboards, [InlineKeyboardButton('بازگشت', callback_data='welcome_handler')]]
    keyboard_markup = InlineKeyboardMarkup(keyboards)
    text = f'نوبت های گرفته شده: ({len(list_user_appointment)})'
    await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=keyboard_markup)


async def appointment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    global list_user_appointment
    appointment = list_user_appointment[int(data)]
    text = f"تارخ نوبت:\n {appointment['from_date'][:10]} {appointment['from_date'][11:16]}\nدر تاریخ \n{appointment['booking_date']} گرفته شده\n"
    keyboards = [[InlineKeyboardButton('لغو نوبت', callback_data=f'remove_appointment_handler-{appointment['id']}')],
                 [InlineKeyboardButton('بازگشت', callback_data='list_user_appointment')]]
    keyboard_markup = InlineKeyboardMarkup(keyboards)
    await context.bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard_markup)


async def remove_appointment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(f'http://localhost:8000/api/user-unbook/{data}') as response:
                if response.status == 200:
                    await list_book_appointment(update, context)
                else:
                    keyboard = [[InlineKeyboardButton('تلاش مجدد', callback_data='welcome_handler')]]
                    update.message.reply_text(text='خطایی رخ داده است مجدد تلاش کنید',
                                              reply_markup=InlineKeyboardMarkup(keyboard))


    except aiohttp.client_exceptions.ClientConnectorError:
        await update.message.reply_text('خطایی در شبکه رخ داده است مجدد تلاش کنید')

async def success_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    text = 'نوبت با موفقیت ثبت شد'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('منو',callback_data='welcome_handler')]])
    await context.bot.edit_message_text(text,chat_id,message_id,reply_markup=keyboard)
if __name__ == '__main__':
    token = config('TOKEN')
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', callback=welcome_handler))
    app.add_handler(CallbackQueryHandler(callback=keyboard_handler))
    app.run_polling()
