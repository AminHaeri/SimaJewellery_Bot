import telebot.types


ADMIN_USERS = ['A_M_I_N_H_A', 'mszoheiri']


def is_user_authorized(message: telebot.types.Message):
    return message.from_user.username in ADMIN_USERS
