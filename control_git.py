"""
control_git.py

Этот модуль предоставляет интерфейс для управления репозиторием Git. 
Функционал включает выполнение основных команд Git, управление ветками, 
работу с удалёнными репозиториями, управление файлом .gitignore и очистку репозитория.
Модуль включает текстовый пользовательский интерфейс для взаимодействия с пользователем.
"""

import os
import subprocess
from datetime import datetime
from colorama import Fore, Back, init
import msvcrt  # Для обработки ввода с клавиатуры на Windows

init(autoreset=True)  # Автоматически сбрасывает стиль после каждой строки

def run_command(command):
    """Выполнить команду и вернуть результат с поддержкой корректной кодировки."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', env={**os.environ, 'LC_ALL': 'C.UTF-8'})
        output = result.stdout + (result.stderr if result.stderr else '')
        return output.strip()
    except UnicodeDecodeError as e:
        return f"[ERROR] Проблема с декодированием вывода команды: {e}"

def run_and_log_add(command):
    """Выполняет команду git add и дополнительно возвращает список добавленных файлов."""
    output = run_command(command)
    added_files = run_command("git diff --cached --name-only")
    return f"{output}\n\n[LOG] Список добавленных файлов:\n{added_files}"
def basic_commands():
    footer = ""
    selected = 0
    while True:
        options = [
            "Статус репозитория",
            "Добавить файлы",
            "Коммит изменений",
            "История коммитов",
            "Просмотр закоммиченных файлов",
            "Удалить файлы из репозитория",
            "Авто коммит всех файлов",
            "Откат к коммиту",
            "Просмотр изменений",
            "Сравнение изменений между коммитами",
            "Удалить файл из последнего коммита",
            "Удалить файлы из индекса",
            "Вернуться в главное меню"
        ]

        os.system('cls' if os.name == 'nt' else 'clear')  # Очистка экрана при каждом обновлении меню
        selected = display_menu(options, "\nОсновные команды:", footer, selected)

        if selected == 0:
            footer = run_command("git status")
        elif selected == 1:
            files = input("Введите файлы или '.' для добавления всех (пустое значение для возврата): ").strip()
            if not files:
                continue
            footer = run_and_log_add(f"git add {files}")
        elif selected == 2:
            message = input("Введите сообщение для коммита (пустое значение для возврата): ").strip()
            if not message:
                continue
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"{message} ({current_time})"
            footer = run_command(f"git commit -m \"{full_message}\"")
        elif selected == 3:
            footer = run_command("git log --oneline --graph")
        elif selected == 4:
            footer = run_command("git ls-tree -r HEAD --name-only")
        elif selected == 5:
            files = input("Введите файлы для удаления из репозитория (через запятую, пустое значение для возврата): ").strip()
            if not files:
                continue
            file_list = [file.strip() for file in files.split(',')]
            footer = ""
            for file in file_list:
                result = run_command(f"git ls-files --error-unmatch {file}")
                if not result.startswith("[ERROR]"):
                    footer += run_command(f"git rm --cached {file}") + ""
                else:
                    footer += f"[ERROR] Файл {file} не найден или не отслеживается."
        elif selected == 6:
            footer = run_command("git add .")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer += "\n" + run_command(f"git commit -m \"Авто коммит ({current_time})\"")
        elif selected == 7:
            commits = run_command("git log --oneline").splitlines()
            print("\nСписок коммитов:")
            for i, commit in enumerate(commits):
                print(f"{i}: {commit}")
            commit_index_input = input("Введите номер коммита для отката (пустое значение для возврата): ").strip()
            if not commit_index_input:
                continue
            try:
                commit_index = int(commit_index_input)
                if 0 <= commit_index < len(commits):
                    commit_hash = commits[commit_index].split()[0]
                    confirm = input(f"Вы уверены, что хотите откатиться к коммиту {commit_hash}? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        footer = run_command(f"git reset --hard {commit_hash}")
                    else:
                        footer = "Операция отката отменена."
                else:
                    footer = "Некорректный выбор коммита."
            except ValueError:
                footer = "Введено некорректное значение."
        elif selected == 8:
            footer = run_command("git diff")
        elif selected == 9:
            commit1 = input("Введите хэш первого коммита (пустое значение для возврата): ").strip()
            if not commit1:
                continue
            commit2 = input("Введите хэш второго коммита (пустое значение для возврата): ").strip()
            if not commit2:
                continue
            footer = run_command(f"git diff {commit1} {commit2}")
        elif selected == 10:
            file_to_remove = input("Введите имя файла для удаления из последнего коммита (пустое значение для возврата): ").strip()
            if not file_to_remove:
                continue
            footer = run_command(f"git reset HEAD^ -- {file_to_remove}")
            footer += "\n" + run_command("git commit --amend --no-edit")
        elif selected == 11:
            files_to_unstage = input("Введите файлы для удаления из индекса (через запятую, пустое значение для возврата): ").strip()
            if not files_to_unstage:
                continue
            file_list = [file.strip() for file in files_to_unstage.split(',')]
            footer = ""
            for file in file_list:
                footer += run_command(f"git reset {file}") + "\n"
        elif selected == 12:
            return footer
def branch_management():
    footer = ""
    selected = 0
    while True:
        options = [
            "Просмотр веток",
            "Создать ветку",
            "Переключиться на ветку",
            "Удалить ветку",
            "Переименовать ветку",
            "Принудительное удаление ветки",
            "Слить ветку",
            "Отменить слияние",
            "Удалить отслеживание удаленной ветки",
            "Создать ветку от определенного коммита",
            "Очистить неактуальные удаленные ветки",
            "Просмотр изменений между ветками",
            "Сравнение изменений между ветками",
            "Вернуться в главное меню"
        ]
        selected = display_menu(options, "\nУправление ветками:", footer, selected)
        if selected == 0:
            footer = run_command("git branch")
        elif selected == 1:
            branch_name = input("Введите название новой ветки: ")
            footer = run_command(f"git branch {branch_name}")
        elif selected == 2:
            branch_name = input("Введите название ветки для переключения: ")
            footer = run_command(f"git checkout {branch_name}")
        elif selected == 3:
            branch_name = input("Введите название ветки для удаления: ")
            footer = run_command(f"git branch -d {branch_name}")
        elif selected == 4:
            branch_name = input("Введите текущее имя ветки: ")
            new_branch_name = input("Введите новое имя ветки: ")
            footer = run_command(f"git branch -m {branch_name} {new_branch_name}")
        elif selected == 5:
            branch_name = input("Введите имя ветки для принудительного удаления: ")
            footer = run_command(f"git branch -D {branch_name}")
        elif selected == 6:
            branch_name = input("Введите имя ветки для слияния с текущей: ")
            footer = run_command(f"git merge {branch_name}")
        elif selected == 7:
            footer = run_command("git merge --abort")
        elif selected == 8:
            footer = run_command("git branch --unset-upstream")
        elif selected == 9:
            commit_hash = input("Введите хэш коммита для создания ветки: ")
            branch_name = input("Введите имя новой ветки: ")
            footer = run_command(f"git checkout -b {branch_name} {commit_hash}")
        elif selected == 10:
            footer = run_command("git remote prune origin")
        elif selected == 11:
            branch1 = input("Введите имя первой ветки: ").strip()
            branch2 = input("Введите имя второй ветки: ").strip()
            footer = run_command(f"git diff {branch1}..{branch2}")
        elif selected == 12:
            branch1 = input("Введите имя первой ветки: ").strip()
            branch2 = input("Введите имя второй ветки: ").strip()
            footer = run_command(f"git log {branch1}..{branch2}")
        elif selected == 13:
            return footer
def remote_management():
    footer = ""
    selected = 0
    while True:
        options = [
            "Просмотр удалённых репозиториев",
            "Добавить удалённый репозиторий",
            "Удалить удалённый репозиторий",
            "Получить изменения (pull)",
            "Отправить изменения (push)",
            "Вернуться в главное меню"
        ]
        selected = display_menu(options, "\nРабота с удалёнными репозиториями:", footer, selected)
        if selected == 0:
            footer = run_command("git remote -v")
        elif selected == 1:
            name = input("Введите имя удалённого репозитория: ")
            url = input("Введите URL удалённого репозитория: ")
            footer = run_command(f"git remote add {name} {url}")
        elif selected == 2:
            name = input("Введите имя удалённого репозитория для удаления: ")
            footer = run_command(f"git remote remove {name}")
        elif selected == 3:
            branch = input("Введите название ветки (по умолчанию 'main'): ") or "main"
            footer = run_command(f"git pull origin {branch}")
        elif selected == 4:
            branch = input("Введите название ветки (по умолчанию 'main'): ") or "main"
            footer = run_command(f"git push origin {branch}")
        elif selected == 5:
            return footer
def gitignore_management():
    footer = ""
    selected = 0
    while True:
        options = [
            "Просмотр .gitignore",
            "Добавить запись в .gitignore",
            "Удалить запись из .gitignore",
            "Вернуться в главное меню"
        ]
        selected = display_menu(options, "\nУправление .gitignore:", footer, selected)
        if selected == 0:
            if os.path.exists(".gitignore"):
                with open(".gitignore", "r", encoding="utf-8") as file:
                    footer = file.read()
            else:
                footer = ".gitignore не найден."
        elif selected == 1:
            entries = input("Введите записи для добавления в .gitignore (через запятую): ")
            with open(".gitignore", "a", encoding="utf-8") as file:
                for entry in entries.split(','):
                    file.write(f"{entry.strip()}\n")
            footer = "Записи добавлены в .gitignore."
        elif selected == 2:
            entry_to_remove = input("Введите запись для удаления из .gitignore: ")
            if os.path.exists(".gitignore"):
                with open(".gitignore", "r", encoding="utf-8") as file:
                    lines = file.readlines()
                with open(".gitignore", "w", encoding="utf-8") as file:
                    for line in lines:
                        if line.strip() != entry_to_remove:
                            file.write(line)
                footer = f"Запись '{entry_to_remove}' удалена из .gitignore."
            else:
                footer = ".gitignore не найден."
        elif selected == 3:
            return footer

def clear_repository():
    """Очистить историю Git и индекс, не трогая физические файлы."""
    confirm = input("Вы уверены, что хотите очистить репозиторий? Все данные и коммиты будут удалены. (yes/no): ").strip().lower()
    if confirm == "yes":
        script_name = os.path.basename(__file__)
        with open(".gitignore", "a", encoding="utf-8") as file:
            file.write(f"{script_name}\n")
        footer = f"Добавлено в .gitignore: {script_name}\n"
        footer += run_command("git rm -r --cached .")
        footer += "\nВсе файлы оставлены в рабочей директории."
        footer += "\n" + run_command("git reset --hard")
        footer += "\nРепозиторий очищен."
        return footer
    else:
        return "Операция отменена."
def display_menu(options, title, footer, selected):
    """Отображение меню с возможностью перемещения стрелками и выводом информации внизу."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + title)
        for i, option in enumerate(options):
            if i == selected:
                print(Back.YELLOW + Fore.BLACK + f"> {option}")
            else:
                print(f"  {option}")
        print("\n" + Fore.MAGENTA + "Результат выполнения команды:")
        print(Fore.GREEN + f"{'-' * 40}\n{footer}\n{'-' * 40}")

        key = msvcrt.getch()
        if key == b'\xe0':  # Обработка стрелок на Windows
            arrow = msvcrt.getch()
            if arrow == b'H':  # Вверх
                selected = (selected - 1) % len(options)
            elif arrow == b'P':  # Вниз
                selected = (selected + 1) % len(options)
        elif key == b'\r':  # Enter
            return selected

def main_menu():
    footer = ""
    selected = 0
    while True:
        options = [
            "Основные команды",
            "Управление ветками",
            "Работа с удалёнными репозиториями",
            "Управление .gitignore",
            "Очистить репозиторий",
            "Выход"
        ]
        selected = display_menu(options, "\nGit Management Menu:", footer, selected)
        if selected == 0:
            footer = basic_commands()
        elif selected == 1:
            footer = branch_management()
        elif selected == 2:
            footer = remote_management()
        elif selected == 3:
            footer = gitignore_management()
        elif selected == 4:
            footer = clear_repository()
        elif selected == 5:
            print("Выход из программы.")
            break

if __name__ == "__main__":
    main_menu()

# Конец файла control_git.py
