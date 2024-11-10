from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd  # Добавляем импорт pandas для работы с DataFrame

# Функция для генерации ссылки
def generate_steam_url(appid, market_hash_name):
    base_url = "https://steamcommunity.com/market/pricehistory/?country=DE&currency=3"
    market_hash_name_encoded = market_hash_name.replace(" ", "%20").replace("|", "%7C")
    
    # Создаем итоговую ссылку
    full_url = f"{base_url}&appid={appid}&market_hash_name={market_hash_name_encoded}"
    return full_url

# Пользователь вводит appid и market_hash_name
appid = input("Введите ID игры (appid): ")
market_hash_name = input("Введите market_hash_name (название предмета): ")

# Генерация ссылки
price_history_url = generate_steam_url(appid, market_hash_name)

# Настройка для видимого режима
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Путь к новому ChromeDriver (укажите здесь обновленный путь)
chrome_driver_path = "C:/Users/User/.cache/selenium/chromedriver/win64/130.0.6723.58/chromedriver.exe"

# Запуск браузера
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Переход на страницу входа
    driver.get("https://store.steampowered.com/login/")

    # Ожидание загрузки страницы и нахождение элементов логина и пароля
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']._2GBWeup5cttgbTw8FM3tfx")))
    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']._2GBWeup5cttgbTw8FM3tfx")))

    # Ввод логина и пароля
    username_input.send_keys("sulatevandrej07")
    password_input.send_keys("0p9o8i7u6yY")
    
    # Отправка формы
    password_input.send_keys(Keys.RETURN)

    # Ожидание успешного входа
    time.sleep(5)

    # Переход на страницу ценовой истории с использованием сгенерированной ссылки
    driver.get(price_history_url)

    # Ожидание загрузки страницы и получения JSON данных
    time.sleep(5)  # Даем время на загрузку данных
    page_source = driver.page_source

    # Парсинг JSON из page_source
    start_index = page_source.find('{')
    end_index = page_source.rfind('}') + 1
    json_data = page_source[start_index:end_index]

    # Преобразование строки JSON в словарь Python
    data = json.loads(json_data)
    # Извлекаем нужные данные (цены и даты)
    prices = data['prices']
    dates, price_values, sales = zip(*prices)

    # Создаем DataFrame для удобной работы с данными
    df = pd.DataFrame({'Date': dates, 'Price': price_values, 'Sales': sales})

    # Преобразуем дату в datetime формат
    df['Date'] = pd.to_datetime(df['Date'], format='%b %d %Y %H: +0')

    # Сохраняем в Excel
    df.to_excel('steam_prices.xlsx', index=False)

    print("Данные успешно сохранены в steam_prices.xlsx")
finally:
    # Закрытие браузера
    driver.quit()

# Визуализация данных
import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных из Excel
df = pd.read_excel('steam_prices.xlsx')

# Преобразование даты в datetime формат (если не сделано ранее)
df['Date'] = pd.to_datetime(df['Date'], format='%b %d %Y %H: +0')

# Создание фигуры и осей
fig, ax1 = plt.subplots(figsize=(12, 6))

# Построение графика для цен на основной оси Y
ax1.set_xlabel('Дата')
ax1.set_ylabel('Цена (€)', color='tab:blue')
ax1.plot(df['Date'], df['Price'], color='tab:blue', label='Цена (€)')
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Создание второй оси Y для количества продаж
ax2 = ax1.twinx()
ax2.set_ylabel('Количество продаж', color='tab:orange')
ax2.bar(df['Date'], df['Sales'].astype(int), color='tab:orange', alpha=0.3, label='Количество продаж')
ax2.tick_params(axis='y', labelcolor='tab:orange')

# Добавление заголовка и легенды
plt.title('Исторические цены и количество продаж')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Отображение графика
plt.show()
