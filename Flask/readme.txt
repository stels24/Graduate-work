# To-Do List Web Application



## Features                                       ## Особенности #

- User registration and authentication            #Регистрация и аутентификация пользователя#
- Create, read, update, and delete tasks          #Создание, чтение, обновление и удаление задач#
- Filter tasks by status (all, active, completed) #Фильтровать задачи по статусу (все, активные, завершенные)#
- Sort tasks by date created or priority          #Сортировка задач по дате создания или приоритету#
- Responsive design using Bootstrap               #Адаптивный дизайн с использованием Bootstrap#

## Installation                                   #Инсталяция приложения"

1. Clone the repository:

```bash
git clone https://github.com/yourusername/todo-list.git
Change into the project directory:

cd todo-list
Create a virtual environment (optional but recommended): #Создание виртуальной среды (необязательно,
                                                         но рекомендуется)#

python -m venv venv
Activate the virtual environment (optional but recommended): #Активация виртуальной среды (необязательно,
                                                             но рекомендуется):#
On Windows:

venv\Scripts\activate
On macOS and Linux:

source venv/bin/activate
Install the required packages:                     #Установите необходимые пакеты#

pip install -r requirements.txt
Set the secret key for the Flask application:      #Установите код для приложения#

export SECRET_KEY=your_secret_key
Replace your_secret_key with a secret key of your choice.  #Замените your_secret_key на секретный ключ по вашему выбору#

Run the database migrations:                        #Запустите миграцию базы данных#

flask db upgrade
Run the application:

flask run
Open your browser and navigate to http://127.0.0.1:5000/.
Usage
Register for an account or log in with an existing account.
Create new tasks by clicking the "New Task" button.
View, update, or delete tasks by clicking the corresponding buttons in the tasks table.
Filter tasks by status using the filter dropdown menu.
Sort tasks by date created or priority using the sort dropdown menu.
Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit
a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for more information.


You can save this content to a file named `readme.txt` in the root directory of your project.