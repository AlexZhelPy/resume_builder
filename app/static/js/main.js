document.addEventListener('DOMContentLoaded', function() {
    // Обработка экспорта в PDF
    document.querySelectorAll('.export-pdf-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const resumeId = this.getAttribute('data-resume-id');

            try {
                // Получаем HTML для PDF
                const response = await fetch(`/resume/${resumeId}/export/html`);
                if (!response.ok) throw new Error('Ошибка получения данных');
                const htmlContent = await response.text();

                // Создаем временный элемент для генерации PDF
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = htmlContent;
                document.body.appendChild(tempDiv);

                // Генерируем PDF
                const pdfBlob = await generatePDF(tempDiv);
                document.body.removeChild(tempDiv);

                // Предлагаем сохранить файл
                savePDF(pdfBlob, `resume_${resumeId}.pdf`);

            } catch (error) {
                console.error('Ошибка при экспорте:', error);
                alert('Произошла ошибка при экспорте резюме');
            }
        });
    });

    // Функция генерации PDF
    async function generatePDF(htmlElement) {
        return new Promise((resolve) => {
            const opt = {
                margin: 0,
                filename: 'resume.pdf',
                image: {
                    type: 'jpeg',
                    quality: 0.98 // Улучшение качества изображений
                },
                html2canvas: {
                    scale: 2, // Увеличение масштаба для лучшего качества
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    letterRendering: true
                },
                jsPDF: {
                    unit: 'mm',
                    format: 'a4',
                    orientation: 'portrait'
                }
            };

            html2pdf().set(opt).from(htmlElement).outputPdf('blob').then(resolve);
        });
    }

    // Функция сохранения PDF
    function savePDF(blob, defaultName) {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = defaultName;
        link.setAttribute('type', 'application/pdf');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    document.querySelectorAll('.delete-item').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить это резюме?')) {
                e.preventDefault();
            }
        });
    });

    // Объявляем все необходимые переменные
    const photoInput = document.getElementById('photo');
    const currentPhotoContainer = document.getElementById('current-photo-container');
    const currentPhoto = document.getElementById('current-photo');
    const removePhotoBtn = document.getElementById('remove-photo-btn');
    const photoPreviewContainer = document.getElementById('photo-preview-container');
    const photoPreview = document.getElementById('photo-preview');

    // Обработка выбора фото
    if (photoInput) {
        photoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentPhoto.src = e.target.result;
                    currentPhotoContainer.style.display = 'block';
                    photoPreview.src = e.target.result;
                    photoPreviewContainer.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Удаление фото
    if (removePhotoBtn) {
        removePhotoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            photoInput.value = '';
            currentPhotoContainer.style.display = 'none';
            photoPreviewContainer.style.display = 'none';
            return false;
        });
    }

    // Обработчики для добавления и удаления элементов
    document.addEventListener('click', function(e) {
        // Добавление курса
        if (e.target.id === 'add-course-btn') {
            const template = document.getElementById('course-template');
            const clone = template.content.cloneNode(true);
            document.getElementById('courses-container').appendChild(clone);
            updatePreview();
        }

        // Добавление языка
        else if (e.target.id === 'add-language-btn') {
            const template = document.getElementById('language-template');
            const clone = template.content.cloneNode(true);
            document.getElementById('languages-container').appendChild(clone);
            updatePreview();
        }

        // Добавление навыка
        else if (e.target.id === 'add-skill-btn') {
            const template = document.getElementById('skill-template');
            const clone = template.content.cloneNode(true);
            document.getElementById('skills-container').appendChild(clone);
            updatePreview();
        }

        // Удаление курса
        else if (e.target.classList.contains('remove-course-btn')) {
            e.preventDefault();
            e.target.closest('.course-item').remove();
            updatePreview();
        }

        // Удаление языка
        else if (e.target.classList.contains('remove-language-btn')) {
            e.preventDefault();
            e.target.closest('.language-item').remove();
            updatePreview();
        }

        // Удаление навыка
        else if (e.target.classList.contains('remove-skill-btn')) {
            e.preventDefault();
            e.target.closest('.skill-item').remove();
            updatePreview();
        }
    });

    // Общая функция обновления предпросмотра
    function updatePreview() {
        // Основная информация
        const firstName = document.getElementById('first_name')?.value || 'Имя';
        const lastName = document.getElementById('last_name')?.value || 'Фамилия';
        document.getElementById('preview-name').textContent = `${firstName} ${lastName}`;

        // Должность
        document.getElementById('preview-position').textContent =
            document.getElementById('position')?.value || 'Желаемая должность';

        // Контакты
        const cityElement = document.getElementById('preview-city');
        const phoneElement = document.getElementById('preview-phone');
        const emailElement = document.getElementById('preview-email');
        const githubElement = document.getElementById('preview-github');

        if (cityElement) cityElement.querySelector('span').textContent =
            document.getElementById('city')?.value || 'Город';
        if (phoneElement) phoneElement.querySelector('span').textContent =
            document.getElementById('phone')?.value || 'Телефон';
        if (emailElement) emailElement.querySelector('span').textContent =
            document.getElementById('email')?.value || 'Email';

        const githubValue = document.getElementById('github')?.value;
        if (githubElement) {
            if (githubValue) {
                githubElement.querySelector('span').textContent = githubValue;
                githubElement.style.display = 'flex';
            } else {
                githubElement.style.display = 'none';
            }
        }

        // О себе
        const aboutValue = document.getElementById('about')?.value;
        const aboutSection = document.getElementById('preview-about-section');
        if (aboutSection) {
            if (aboutValue) {
                document.getElementById('preview-about').textContent = aboutValue;
                aboutSection.style.display = 'block';
            } else {
                aboutSection.style.display = 'none';
            }
        }

        // Навыки
        const skillItems = document.querySelectorAll('.skill-item');
        const skillsContainer = document.getElementById('preview-skills');
        const skillsSection = document.getElementById('preview-skills-section'); // Секция навыков

        if (skillsContainer && skillsSection) {
            skillsContainer.innerHTML = ''; // Очищаем контейнер навыков
            let hasSkills = false; // Флаг наличия навыков

            skillItems.forEach(item => {
                const name = item.querySelector('.skill-name')?.value || '';
                const level = item.querySelector('.skill-level')?.value || 'beginner';

                if (name.trim() !== '') { // Проверяем, введён ли хотя бы один символ
                    hasSkills = true; // Устанавливаем флаг
                    const levelText = {
                        'beginner': 'Начальный',
                        'basic': 'Базовый',
                        'intermediate': 'Опытный',
                        'professional': 'Профессиональный'
                    }[level] || level;

                    const skillElement = document.createElement('div');
                    skillElement.className = 'skill-preview-item';
                    skillElement.innerHTML = `${name}: ${levelText}`;
                    skillsContainer.appendChild(skillElement);
                }
            });

            // Отображаем или скрываем секцию навыков
            skillsSection.style.display = hasSkills ? 'block' : 'none';
        }


        // Образование
        const educationValue = document.getElementById('education')?.value;
        const educationSection = document.getElementById('preview-education-section');
        if (educationSection) {
            if (educationValue) {
                document.getElementById('preview-education').textContent = educationValue;
                educationSection.style.display = 'block';
            } else {
                educationSection.style.display = 'none';
            }
        }

        // Опыт работы
        const experienceValue = document.getElementById('experience')?.value;
        const experienceSection = document.getElementById('preview-experience-section');
        if (experienceSection) {
            if (experienceValue) {
                document.getElementById('preview-experience').textContent = experienceValue;
                experienceSection.style.display = 'block';
            } else {
                experienceSection.style.display = 'none';
            }
        }

        // Курсы
        const courseItems = document.querySelectorAll('.course-item');
        const coursesContainer = document.getElementById('preview-courses-container');
        if (coursesContainer) {
            coursesContainer.innerHTML = '';

            let hasCourses = false;
            courseItems.forEach(item => {
                const name = item.querySelector('.course-name')?.value;
                const org = item.querySelector('.course-org')?.value;
                const year = item.querySelector('.course-year')?.value;

                if (name && name.trim() !== '' || org && org.trim() !== '') {
                    hasCourses = true;
                    const courseElement = document.createElement('div');
                    courseElement.className = 'course-preview-item';
                    courseElement.innerHTML = `
                        <strong>${name}</strong> (${org})<br>
                        ${year ? 'Год окончания: ' + year : ''}
                    `;
                    coursesContainer.appendChild(courseElement);
                }
            });

            document.getElementById('preview-courses-section').style.display =
                hasCourses ? 'block' : 'none';
        }

        // Языки
        const languageItems = document.querySelectorAll('.language-item');
        const languagesContainer = document.getElementById('preview-languages-container');
        if (languagesContainer) {
            languagesContainer.innerHTML = '';

            let hasLanguages = false;
            languageItems.forEach(item => {
                const name = item.querySelector('.language-name')?.value;
                const level = item.querySelector('.language-level')?.value;

                if (name && name.trim() !== '') {
                    hasLanguages = true;
                    const levelText = {
                        'A1': 'A1 - Начальный',
                        'A2': 'A2 - Базовый',
                        'B1': 'B1 - Средний',
                        'B2': 'B2 - Выше среднего',
                        'C1': 'C1 - Продвинутый',
                        'C2': 'C2 - Владение в совершенстве'
                    }[level] || level || 'Не указан';

                    const languageElement = document.createElement('div');
                    languageElement.className = 'language-preview-item';
                    languageElement.innerHTML = `<strong>${name}</strong>: ${levelText}`;
                    languagesContainer.appendChild(languageElement);
                }
            });

            document.getElementById('preview-languages-section').style.display =
                hasLanguages ? 'block' : 'none';
        }
    }

    // Инициализация обработчиков для всех полей формы
    const formInputs = document.querySelectorAll('.resume-form input, .resume-form textarea, .resume-form select');
    formInputs.forEach(input => {
        input.addEventListener('input', updatePreview);
        input.addEventListener('change', updatePreview);
    });

    // Инициализация предпросмотра при загрузке
    updatePreview();
});