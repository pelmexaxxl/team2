team2/
├── logs/                      # Каталог для хранения логов работы бота
├── src/                       # Основной каталог с исходным кодом
│   ├── bot.py                 # Точка входа в приложение, запуск бота
│   ├── config.py              # Конфигурационный файл (токен бота, параметры БД)
│   ├── db.py                  # Модуль для взаимодействия с базой данных PostgreSQL
│   │
│   ├── handlers/              # Пакет с обработчиками команд и сообщений
│   │   ├── admin.py           # Обработчик для создания опросов с использованием FSM
│   │   └── respond.py         # Обработчик для прохождения опросов пользователями
│   │
│   └── services/              # Пакет с сервисными модулями
│       └── poll_manager.py    # Управление рассылкой опросов участникам чата в личные сообщения
│
├── .gitignore                 # Файл, определяющий файлы и папки, игнорируемые Git
├── Dockerfile                 # Сценарий для создания Docker-образа приложения
├── README.md                  # Документация проекта
├── docker-compose.yml         # Файл для оркестрации контейнеров с использованием Docker Compose
└── requirements.txt           # Список зависимостей проекта
