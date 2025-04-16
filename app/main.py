import os
import time
import pdfkit
from pathlib import Path
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional, Dict, Any, Generator
from . import models
from .database import SessionLocal, engine, get_db
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import _TemplateResponse
from tempfile import NamedTemporaryFile

# Инициализация базы данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resume Builder API",
    description="API для создания и управления резюме",
    version="1.0.0"
)

# Конфигурация middleware и статических файлов
app.add_middleware(SessionMiddleware, secret_key="dfgfdgdfgdfghghgghkrtyrtasd")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/static/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")

templates = Jinja2Templates(directory="app/templates")


class Config:
    """Конфигурация приложения для загрузки файлов"""
    UPLOAD_FOLDER = Path("app/static/uploads/photos")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB


os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> _TemplateResponse:
    """
    Главная страница приложения.

    Args:
        request: Request объект FastAPI

    Returns:
        HTMLResponse: Рендер главной страницы
    """
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/create", response_class=HTMLResponse)
async def create_resume_form(request: Request) -> _TemplateResponse:
    """
    Отображает форму создания нового резюме.

    Args:
        request: Request объект FastAPI

    Returns:
        HTMLResponse: Форма создания резюме с текущим годом для выбора дат
    """
    current_year = date.today().year
    return templates.TemplateResponse(
        "create.html",
        {
            "request": request,
            "current_year": current_year,
            "range": range
        }
    )


@app.post("/create", response_class=HTMLResponse)
async def create_resume(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        birth_day: Optional[str] = Form(None),
        birth_month: Optional[str] = Form(None),
        birth_year: Optional[str] = Form(None),
        city: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        github: Optional[str] = Form(None),
        position: str = Form(...),
        about: Optional[str] = Form(None),
        skill_name: List[str] = Form([]),
        skill_level: List[str] = Form([]),
        education: str = Form(...),
        experience: Optional[str] = Form(None),
        photo: Optional[UploadFile] = File(None),
        course_name: List[str] = Form([]),
        course_organization: List[str] = Form([]),
        course_year: List[str] = Form([]),
        language_name: List[str] = Form([]),
        language_level: List[str] = Form([]),
        db: Session = Depends(get_db)
) -> Response:
    """
    Обрабатывает отправку формы создания резюме.

    Args:
        request: Request объект FastAPI
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        birth_day: День рождения (опционально)
        birth_month: Месяц рождения (опционально)
        birth_year: Год рождения (опционально)
        city: Город проживания
        email: Электронная почта
        phone: Номер телефона
        github: Ссылка на GitHub профиль (опционально)
        position: Желаемая должность
        about: Информация о себе (опционально)
        skill_name: Список названий навыков
        skill_level: Список уровней навыков
        education: Образование
        experience: Опыт работы (опционально)
        photo: Загружаемое фото (опционально)
        course_name: Список названий курсов
        course_organization: Список организаций курсов
        course_year: Список годов окончания курсов
        language_name: Список названий языков
        language_level: Список уровней владения языками
        db: Сессия базы данных

    Returns:
        RedirectResponse: Редирект на просмотр резюме или форму с ошибками
    """
    try:
        # Обработка и валидация данных
        birth_date = None
        if birth_day and birth_month and birth_year:
            birth_date = date(
                year=int(birth_year),
                month=int(birth_month),
                day=int(birth_day)
            )

        photo_path = await handle_photo_upload(photo)

        skills = process_skills(skill_name, skill_level)
        courses = process_courses(course_name, course_organization, course_year)
        languages = process_languages(language_name, language_level)

        # Создание резюме
        resume_data = {
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "photo_path": photo_path,
            "city": city,
            "email": email,
            "phone": phone,
            "github": github,
            "position": position,
            "about": about,
            "skills": skills,
            "education": education,
            "experience": experience,
            "courses": courses,
            "languages": languages,
            "created_at": date.today()
        }

        db_resume = models.Resume(**resume_data)
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        return RedirectResponse(f"/resume/{db_resume.id}", status_code=303)

    except Exception as e:
        current_year = date.today().year
        error_msg = f"Ошибка при сохранении резюме: {str(e)}"
        print(error_msg)
        return templates.TemplateResponse(
            "create.html",
            {
                "request": request,
                "error": error_msg,
                "current_year": current_year,
                "range": range,
                "form_data": request.form
            },
            status_code=500
        )


async def handle_photo_upload(photo: Optional[UploadFile]) -> Optional[str]:
    """
    Обрабатывает загрузку фотографии пользователя.

    Args:
        photo: Загружаемый файл фотографии

    Returns:
        Optional[str]: Путь к сохраненному файлу или None

    Raises:
        ValueError: Если файл слишком большой или не является изображением
    """
    if not photo or not photo.content_type.startswith('image/'):
        return None

    try:
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_ext = Path(photo.filename).suffix.lower()
        filename = f"{int(time.time())}{file_ext}"
        file_path = Config.UPLOAD_FOLDER / filename

        if photo.size > Config.MAX_CONTENT_LENGTH:
            raise ValueError("Файл слишком большой")

        with open(file_path, "wb") as buffer:
            buffer.write(await photo.read())

        return f"photos/{filename}"
    except Exception as e:
        raise ValueError(f"Ошибка загрузки фото: {str(e)}")


def process_skills(names: List[str], levels: List[str]) -> List[Dict[str, str]]:
    """Обрабатывает и валидирует список навыков."""
    return [{"name": name, "level": level}
            for name, level in zip(names, levels)
            if name and level]


def process_courses(
        names: List[str],
        orgs: List[str],
        years: List[str]
) -> List[Dict[str, Any]]:
    """Обрабатывает и валидирует список курсов."""
    return [{"name": name, "organization": org, "year": year}
            for name, org, year in zip(names, orgs, years)
            if name and org and year]


def process_languages(names: List[str], levels: List[str]) -> List[Dict[str, str]]:
    """Обрабатывает и валидирует список языков."""
    return [{"name": name, "level": level}
            for name, level in zip(names, levels)
            if name and level]


@app.post("/resume/{resume_id}/delete_photo", response_class=RedirectResponse)
async def delete_photo(
        resume_id: int,
        db: Session = Depends(get_db)
) -> RedirectResponse:
    """
    Удаляет фотографию из резюме.

    Args:
        resume_id: ID резюме
        db: Сессия базы данных

    Returns:
        RedirectResponse: Перенаправляет на страницу редактирования резюме

    Raises:
        HTTPException: Если резюме не найдено
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    if resume.photo_path:
        photo_path = Config.UPLOAD_FOLDER / resume.photo_path.split('/')[-1]
        if photo_path.exists():
            photo_path.unlink()
        resume.photo_path = None
        db.commit()

    return RedirectResponse(f"/resume/{resume_id}")


@app.get("/resumes", response_class=HTMLResponse)
async def list_resumes(
        request: Request,
        db: Session = Depends(get_db)
) ->  _TemplateResponse:
    """
    Отображает список всех резюме.

    Args:
        request: Request объект FastAPI
        db: Сессия базы данных

    Returns:
        HTMLResponse: Страница со списком резюме
    """
    resumes = db.query(models.Resume).order_by(models.Resume.created_at.desc()).all()
    return templates.TemplateResponse("list.html", {
        "request": request,
        "resumes": resumes
    })


@app.get("/resume/{resume_id}", response_class=HTMLResponse)
async def view_resume(
        request: Request,
        resume_id: int,
        db: Session = Depends(get_db)
) ->  _TemplateResponse:
    """
    Отображает детальную страницу резюме.

    Args:
        request: Request объект FastAPI
        resume_id: ID резюме
        db: Сессия базы данных

    Returns:
        HTMLResponse: Страница просмотра резюме

    Raises:
        HTTPException: Если резюме не найдено
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    return templates.TemplateResponse("view.html", {
        "request": request,
        "resume": resume
    })


@app.get("/resume/{resume_id}/edit", response_class=HTMLResponse)
async def edit_resume_form(
        request: Request,
        resume_id: int,
        db: Session = Depends(get_db)
) ->  _TemplateResponse:
    """
    Отображает форму редактирования резюме.

    Args:
        request: Request объект FastAPI
        resume_id: ID резюме
        db: Сессия базы данных

    Returns:
        HTMLResponse: Форма редактирования резюме

    Raises:
        HTTPException: Если резюме не найдено
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    current_year = date.today().year
    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "resume": resume,
            "current_year": current_year,
            "range": range
        }
    )

@app.post("/resume/{resume_id}/edit", response_class=HTMLResponse)
async def update_resume(
        request: Request,
        resume_id: int,
        first_name: str = Form(...),
        last_name: str = Form(...),
        birth_day: str = Form(None),
        birth_month: str = Form(None),
        birth_year: str = Form(None),
        city: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        github: str = Form(None),
        position: str = Form(...),
        about: str = Form(None),
        skill_name: list[str] = Form([]),
        skill_level: list[str] = Form([]),
        education: str = Form(...),
        experience: str = Form(None),
        photo: UploadFile = File(None),
        course_name: list[str] = Form([]),
        course_organization: list[str] = Form([]),
        course_year: list[str] = Form([]),
        language_name: list[str] = Form([]),
        language_level: list[str] = Form([]),
        db: Session = Depends(get_db)
):
    try:
        resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Резюме не найдено")

        # Обработка даты рождения
        birth_date = None
        if birth_day and birth_month and birth_year:
            birth_date = date(
                year=int(birth_year),
                month=int(birth_month),
                day=int(birth_day)
            )

        # Обработка фото
        if photo and photo.content_type.startswith('image/'):
            try:
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file_ext = Path(photo.filename).suffix.lower()
                filename = f"{int(time.time())}{file_ext}"
                file_path = Config.UPLOAD_FOLDER / filename

                if photo.size > Config.MAX_CONTENT_LENGTH:
                    raise ValueError("Файл слишком большой")

                with open(file_path, "wb") as buffer:
                    buffer.write(await photo.read())

                # Удаляем старое фото если оно есть
                if resume.photo_path:
                    old_photo = Config.UPLOAD_FOLDER / resume.photo_path.split('/')[-1]
                    if old_photo.exists():
                        old_photo.unlink()

                resume.photo_path = f"photos/{filename}"
            except Exception as e:
                raise ValueError(f"Ошибка загрузки фото: {str(e)}")

        skills = []
        for name, level in zip(skill_name, skill_level):
            if name and level:
                skills.append({
                    "name": name,
                    "level": level
                })

        # Обработка курсов
        courses = []
        for name, org, year in zip(course_name, course_organization, course_year):
            if name and org and year:
                courses.append({
                    "name": name,
                    "organization": org,
                    "year": year
                })

        # Обработка языков
        languages = []
        for name, level in zip(language_name, language_level):
            if name and level:
                languages.append({
                    "name": name,
                    "level": level
                })

        # Обновляем данные резюме
        resume.first_name = first_name
        resume.last_name = last_name
        resume.birth_date = birth_date
        resume.city = city
        resume.email = email
        resume.phone = phone
        resume.github = github
        resume.position = position
        resume.about = about
        resume.skills = skills
        resume.education = education
        resume.experience = experience
        resume.courses = courses
        resume.languages = languages

        db.commit()
        db.refresh(resume)

        return RedirectResponse(f"/resume/{resume.id}", status_code=303)

    except Exception as e:
        current_year = date.today().year
        error_msg = f"Ошибка при обновлении резюме: {str(e)}"
        print(error_msg)
        return templates.TemplateResponse(
            "edit.html",
            {
                "request": request,
                "error": error_msg,
                "resume": resume,
                "current_year": current_year,
                "range": range
            },
            status_code=500
        )


@app.post("/resume/{resume_id}/delete", response_class=RedirectResponse)
async def delete_resume(
        resume_id: int,
        db: Session = Depends(get_db)
) -> RedirectResponse:
    """
    Удаляет резюме из системы.

    Args:
        resume_id: ID резюме
        db: Сессия базы данных

    Returns:
        RedirectResponse: Перенаправляет на список резюме

    Raises:
        HTTPException: Если резюме не найдено
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    # Удаляем связанное фото
    if resume.photo_path:
        photo_path = Config.UPLOAD_FOLDER / resume.photo_path.split('/')[-1]
        if photo_path.exists():
            photo_path.unlink()

    db.delete(resume)
    db.commit()

    return RedirectResponse("/resumes", status_code=303)


@app.get("/resume/{resume_id}/export/html", response_class=HTMLResponse)
async def get_resume_html_for_pdf(
        resume_id: int,
        db: Session = Depends(get_db)
) -> HTMLResponse:
    """
    Генерирует HTML для экспорта резюме в PDF.

    Args:
        resume_id: ID резюме
        db: Сессия базы данных

    Returns:
        HTMLResponse: HTML версия резюме для конвертации в PDF

    Raises:
        HTTPException: Если резюме не найдено
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    return HTMLResponse(
        content=templates.get_template("pdf_export.html").render(
            {"request": Request({"type": "http"}), "resume": resume}
        )
    )


@app.get("/resume/{resume_id}/export/pdf")
async def export_resume_pdf(
        resume_id: int,
        db: Session = Depends(get_db)
) -> FileResponse:
    """
    Экспортирует резюме в PDF формате.

    Args:
        resume_id: ID резюме
        db: Сессия базы данных

    Returns:
        FileResponse: PDF файл с резюме

    Raises:
        HTTPException: Если резюме не найдено
        RuntimeError: Если произошла ошибка при генерации PDF
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    options = {
        'page-size': 'A4',
        'margin-top': '15mm',
        'margin-right': '20mm',
        'margin-bottom': '15mm',
        'margin-left': '20mm',
        'encoding': 'UTF-8',
        'quiet': '',
        'enable-local-file-access': '',
        'footer-center': '[page]',
        'no-outline': None,
        'print-media-type': None,
        'disable-smart-shrinking': None,
        'header-spacing': '0',
        'footer-spacing': '0'
    }

    try:
        html_content = templates.get_template("pdf_export.html").render(
            {"request": Request({"type": "http"}), "resume": resume}
        )

        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdfkit.from_string(html_content, tmp.name, options=options)
            return FileResponse(
                tmp.name,
                media_type='application/pdf',
                filename=f"resume_{resume.first_name}_{resume.last_name}.pdf"
            )
    except Exception as e:
        raise RuntimeError(f"Ошибка при генерации PDF: {str(e)}") from e

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)