import pandas as pd, time, glob, re, getpass, platform, telebot, requests, random, numpy as np
from datetime import datetime, timedelta
from mysql.connector import Error
from tqdm import tqdm
import os
from dotenv import load_dotenv

#Паттерны
load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("CHAT_ID")
re_1 = r'[^0-9a-zA-Z]'                                                                                                   # Регулярное выражение для отсева специаильных символов в артикуле
re_2 = r'[^0-9a-zA-Z;]'                                                                                                  # Регулярка для чистки мусора в наименовании моделей

def SendTelegram(status):                                                                                                # Модуль telegram бота (надеюсь, вы не против безобидного промышленного шпионажа)
	# Получение информации о компьютере
	UserName = getpass.getuser()                                                                                         # Имя пользователя (обычно оно User - не информативно)
	CompName = platform.node()                                                                                           # Имя компьютера
	if status == "try": # Если связь с телегой установлена
		bot.send_message(chat_id, date+" пользователь "+UserName+" ("+CompName+") успешно воспользовался скриптом для заполнения параметров товаров по артикулам") #Отправка сообщения
	elif status == "except1": # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: " + date+" пользователь "+UserName+" ("+CompName+") неудачно запустил скрипт - похоже, в папке не хватает файлов или их имена поменялись") #Отправка сообщения
	elif status == "except2": # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: " + date+" пользователь "+UserName+" ("+CompName+") неудачно запустил скрипт - кажется, они спалили, что я не программист: тикай с городу") #Отправка сообщения
	elif status == "except3":  # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: " + date + " пользователь " + UserName + " (" + CompName + ") неудачно запустил скрипт - скрипт не нашёл json файл")  # Отправка сообщения
def InputMARK(x):                                                                                                        # Функция для выбора марок автомобилей
	global ColomnModels
	List = []; Marks = []; Country = []; Models = []                                                                     # Создаём списки, которые, собственно, и будут наполнены данными по маркам и моделям
	for m, mc in zip(Mark_list, Country_list):                                                                           # Итерировать будем сразу два списка через zip, потому что на вход у нас названия на латиннице, а на выходе хотим на киррилице
		pattern = re.compile(r'\b{}\b'.format(m), re.IGNORECASE)                                                         # Эта регулярка определяет метод поиска по целым словам: \b\b - обозначаются границы слова, но работает это медленно и надо будет подумать на что поменять
		if bool(pattern.search(x.lower())):                                                                              # Дальше проверяем соответсвия паттерна мешанине накорябанной в файле поставщика
			Marks.append(m); Country.append(mc)                                                                          # При удачном вхождении забираем аналог имени из json в список марок
			print()
			Auto = AllAuto[AllAuto['name'] == str(m)]["models"].values.tolist()[0]                                       # Теперь смотрим какие модели валидны для конкретно этой марки автомобиля
			for key in Auto:
				pattern = re.compile(r'\b{}\b'.format(key['name']), re.IGNORECASE)                                       # Опрять же нам нужны целые слова и фразы: разумеется, метод "for x in list" будет работать в десятки раз быстрее, но при этом будет находить лишние вхождения внутри слова
				if bool(pattern.search(x.lower())): Models.append(key['name']); break                                    # Добавляем в список моделей удачное вхождение
			break
	List = [Marks, Country, Models]                                                                                      # Объединяем в списки списков (списки списов можно удобно распарсить пандами не прибегая к насилию и не городить огород из lambda-функций)
	print(List)
	return List
def GetAuto():
	global Mark_list, Country_list
	try:
		AllAuto = pd.read_json("cars.json")                                                                                  # В моделях разбираюсь плохо, так что будем парсить какой-то рандомный файл из интернета для определения марок и моделей авто
		AllAuto.loc[len(AllAuto.index)] = ['КАМАЗ', 'Камаз', 'Камаз', False, 'Россия', []]                                   # Можем добавить в json свои модели автомобилей или занести "кривые" названия от поставщиков (в данном файле точно отсутсвуют грузовики и мотоциклы - это автор сделал платной услугой)
		Mark_list = list(filter(None, AllAuto.name.tolist()))                                                                # Конвертируем словарь по моделям авто в список для поиска
		Country_list = list(filter(None, AllAuto.country.tolist()))                                                          # Конвертируем словарь по странам производства авто
		return AllAuto
	except Error as e:
		print(f"The error '{e}' occurred");	print("Не удалось найти json файл с марками авто"); SendTelegram("except3"); time.sleep(5); exit()
def GetFile(FileLocation):
	global AllAuto
	GroupFile = [item for item in glob.glob(FileLocation)]                                                               # Собираем файлы в список
	for Filename in tqdm(GroupFile):                                                                                     # Вводные для progress bar
		if not 'Результат валидации' in str(Filename):
			print(Filename, "Началась загрузка excel файла: ", datetime.time(datetime.now()))
			sample = pd.DataFrame(pd.read_excel(Filename, usecols=['Номер телефона', 'Автомобиль', 'Сумма всего']))               # Читаем файл с заданием и получаем колонку с артикулами
			print("Все файлы загружены, начинаю конвертацию и расчёты")
			AllAuto = GetAuto()
			Create_dict()                                                                                                # Функция для создания словарей
			Combineted(Filename, sample, AllAuto)                                                                        # Функция для сборки шаблона
def Create_dict():
	global dict_auto
	dict_auto = {'VOLVO': 'Volvo', 'VW': 'Volkswagen', 'MB': 'Mercedes-Benz', 'CHERYEXEED LX': 'CHERY EXEED LX', 'CHERYEXEED TXL': 'CHERY EXEED TXL'}                      # Словарь ключевых слов - один из методов ручного генерирования костылей для выравнивания файлов поставщиков - систему можно настроить на обучение
def multiple_replace(dict, text):                                                                                        # Модуль для массовой замены слов по словарю (проблема в том, что названия ключей могут находится и внутри слова - в таком случае простая замена replace.dict(x) не сработает
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))                                                     # Регулярка для определения границ слов
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)                                                # Поиск по ключу и замена слов в text
def Combineted(Filename, sample, AllAuto):
	try:
		sample['Марка и модель (замены)'] = sample.apply(lambda x: multiple_replace(dict_auto, x['Автомобиль']), axis=1) # Собственно, замены по словарю
		sample['Марка и модель'] = sample['Марка и модель (замены)'].apply(lambda x: InputMARK(x))                       # Отправляем получившуюся кашу на доработку: в ответ получим список списков [[], []] с "чистыми" марками и моделями авто
		sample['Марка'] = sample['Марка и модель'].apply(lambda x: ';'.join(x[0]))                                       # Это идеальный вариант, когда в все марки определились скриптом по json файлу
		sample['Страна'] = sample['Марка и модель'].apply(lambda x: ';'.join(x[1]))                                      # Это идеальный вариант, когда в все марки определились скриптом по json файлу
		sample['Модель'] = sample['Марка и модель'].apply(lambda x: ';'.join(x[2]))                                      # Это идеальный вариант, когда в все марки определились скриптом по json файлу
		group_client = sample.groupby([sample['Страна']])['Номер телефона'].count().reset_index()                        # Группировка по странам (машино-заезды)
		group_unique_client = sample.groupby([sample['Страна']])['Номер телефона'].nunique().reset_index()               # Группировка по странам (уникальные клиенты)
		sample_group_client = sample.groupby([sample['Страна'], sample['Марка']])['Номер телефона'].count().reset_index() # Группировка по странам и маркам (машино-заезды)
		sample_group_group_unique_client = sample.groupby([sample['Страна'], sample['Марка']])['Номер телефона'].nunique().reset_index() # Группировка по странам и маркам (уникальные клиенты)
		try:
			with pd.ExcelWriter(Filename, engine='openpyxl', mode='a') as writer:  # Дополнение excel файла новыми листами
				try:
					sample.to_excel(writer, sheet_name='Расшифровка', index=False)
					group_client.to_excel(writer, sheet_name='По странам', index=False)
					group_unique_client.to_excel(writer, sheet_name='По странам (уник.)', index=False)
					sample_group_client.to_excel(writer, sheet_name='По маркам', index=False)
					sample_group_group_unique_client.to_excel(writer, sheet_name='По странам и маркам (уник.)', index=False)
				except: pass
		except:	print("В файле" + Filename + " уже присутствуют листы с аналитикой :("); time.sleep(5)
	except Error as e:
		print(f"The error '{e}' occurred"); print("Похоже, скрипт споткнулся и умер - пните разработчика, похоже он подкинул вам паль. Инициирую самоуничтожение через 5 секунд."); SendTelegram("except2"); time.sleep(10); exit()

GetFile('*.xlsx')