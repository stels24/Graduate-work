# To-Do List Web Application



## Особенности                                       

- Регистрация и аутентификация пользователя
- Создание, чтение, обновление и удаление задач
- Фильтровать задачи по статусу (все, активные, завершенные)
- Сортировка задач по дате создания или приоритету#
- Адаптивный дизайн с использованием Bootstrap

## Инсталяция приложения

1. Clone the repository:

```bash
git clone https://github.com/yourusername/todo-list.git
Перейдите в каталог проекта:

cd todo-list
Создание виртуальной среды (необязательно, но рекомендуется): 
                                                         
python -m venv venv

Активация виртуальной среды (необязательно, но рекомендуется): 
                                                            
On Windows:

venv\Scripts\activate
On macOS and Linux:

source venv/bin/activate
Install the required packages:                    

pip install -r requirements.txt
Установите секретный ключ для приложения Flask:     

export SECRET_KEY=your_secret_key
Replace your_secret_key with a secret key of your choice. 

Запустите миграцию базы данных:                       

обновление flask db
Запустите приложение:

flask run
Откройте свой браузер и перейдите по ссылке http://127.0.0.1:5000 /.
Использование
Зарегистрируйтесь для создания учетной записи или войдите в систему с существующей учетной записью.
Создайте новые задачи, нажав на кнопку "Новая задача".
Просматривайте, обновляйте или удаляйте задачи, нажимая соответствующие кнопки в таблице задач.
Отфильтруйте задачи по статусу, используя раскрывающееся меню "Фильтр".
Сортируйте задачи по дате создания или приоритету, используя раскрывающееся меню "Сортировка".

License
This project is licensed under the MIT License. See the LICENSE file for more information.


You can save this content to a file named `readme.txt` in the root directory of your project.
