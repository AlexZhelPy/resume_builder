# Resume Builder 🚀

**Конструктор резюме** - это веб-приложение для создания, редактирования и экспорта резюме в PDF формате.

## 📌 Основные возможности

- 📝 Создание резюме с полной информацией о кандидате
- ✏️ Редактирование существующих резюме
- 🗂️ Управление списком всех резюме
- 📊 Просмотр резюме в удобном формате
- 🖨️ Экспорт резюме в PDF
- 📁 Загрузка фотографии профиля

## 🛠 Технологии

- **Backend**: Python + FastAPI
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (с возможностью легкого перехода на PostgreSQL)
- **PDF Generation**: pdfkit + wkhtmltopdf
- **Templating**: Jinja2

## ⚙️ Установка и запуск

### Требования
- Python 3.9+
- wkhtmltopdf (для генерации PDF)

### Установка

1. Клонируйте репозиторий:
```bash
    git clone https://github.com/AlexZhelPy/resume_builder.git
    cd resume-builder
```
    
2. Создайте и активируйте виртуальное окружение:

```bash
    Copy
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate     # Windows
```
    
3. Установите зависимости:

```bash
    Copy
    pip install -r requirements.txt
```
4. Установите wkhtmltopdf:

Ubuntu/Debian:

```bash
    Copy
    sudo apt-get install wkhtmltopdf
```
MacOS:

```bash
    Copy
    brew install wkhtmltopdf
```
Windows: Скачать с официального сайта

5. Запустите приложение:

```bash
    Copy
    uvicorn main:app --reload
```
Приложение будет доступно по адресу: http://localhost:8000

🗂 Структура проекта
```Copy
resume-builder/
├── app/
│   ├── static/          # Статические файлы (CSS, JS, изображения)
│   ├── templates/       # HTML шаблоны
│   ├── main.py          # Основной файл приложения
│   ├── database.py      # Настройки базы данных
│   └── models.py        # Модели данных
├── requirements.txt     # Зависимости
└── README.md            # Этот файл
```
```
🌐 API Endpoints
Метод	Путь	Описание
GET	/	Главная страница
GET	/create	Форма создания резюме
POST	/create	Обработка формы создания
GET	/resumes	Список всех резюме
GET	/resume/{id}	Просмотр резюме
GET	/resume/{id}/edit	Форма редактирования
POST	/resume/{id}/edit	Обновление резюме
POST	/resume/{id}/delete	Удаление резюме
GET	/resume/{id}/export/pdf	Экспорт в PDF
```
