from telegrambot import *


def main():
    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
