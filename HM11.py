from collections import UserDict
from datetime import datetime


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.page_size = 5

    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self):
        keys = list(self.data.keys())
        total_records = len(keys)
        current_page = 0

        while current_page * self.page_size < total_records:
            start_index = current_page * self.page_size
            end_index = start_index + self.page_size
            page_keys = keys[start_index:end_index]
            yield [self.data[key] for key in page_keys]
            current_page += 1


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def days_to_birthday(self):
        if self.birthday.value is None:
            return None

        today = datetime.now().date()
        next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()

        if next_birthday < today:
            next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()

        return (next_birthday - today).days


class Field:
    def __init__(self, value=None):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value=None):
        super().__init__(value)
        self.validate_phone_number()

    def validate_phone_number(self):
        if self.value is not None and not str(self.value).isdigit():
            raise ValueError("Invalid phone number")


class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)
        self.validate_birthday()

    def validate_birthday(self):
        if self.value is not None:
            try:
                datetime.strptime(self.value, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid birthday format")


USERS = AddressBook()


def error_handler(func):
    def inner(*args):
        try:
            result = func(*args)
            return result
        except KeyError:
            return "User not found"
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter user name"

    return inner


def hello_user():
    return "How can I help you?"


def unknown_command():
    return "unknown_command"


def exit_command():
    return "Goodbye!"


@error_handler
def add_user(name, phone, birthday=None):
    if name in USERS:
        old_phone = USERS[name].phones[0].value
        USERS[name].phones[0].value = phone

        if birthday:
            USERS[name].birthday.value = birthday

        return f"Користувач {name} оновлений! Новий телефон: {phone}. Старий телефон: {old_phone}"
    else:
        record = Record(name, birthday)
        record.add_phone(phone)
        USERS.add_record(record)
        return f"User {name} added!"


@error_handler
def change_phone(name, phone):
    if name in USERS:
        old_phone = USERS[name].phones[0].value
        USERS[name].phones[0].value = phone
        return f"{name} має новий телефон: {phone} Старий номер: {old_phone}"
    else:
        return "User not found"


def show_all():
    if USERS:
        result = ""
        for records in USERS.iterator():
            for record in records:
                phones = ', '.join([phone.value for phone in record.phones])
                birthday = record.birthday.value if record.birthday.value else "Not specified"
                result += f"Name: {record.name.value}, Phones: {phones}, Birthday: {birthday}\n"
        return result
    else:
        return "No users found"


@error_handler
def show_phone(name):
    if name in USERS:
        record = USERS[name]
        phones = ', '.join([phone.value for phone in record.phones])
        return f"Phone number(s) for {name}: {phones}"
    else:
        return "User not found"


@error_handler
def show_birthday(name):
    if name in USERS:
        record = USERS[name]
        birthday = record.birthday.value if record.birthday.value else "Not specified"
        return f"Birthday for {name}: {birthday}"
    else:
        return "User not found"


@error_handler
def days_to_birthday(name):
    if name in USERS:
        record = USERS[name]
        days = record.days_to_birthday()
        if days is None:
            return f"No birthday specified for {name}"
        else:
            return f"Days until {name}'s birthday: {days}"
    else:
        return "User not found"


HANDLERS = {
    "hello": hello_user,
    "add": add_user,
    "change": change_phone,
    "show all": show_all,
    "show phone": show_phone,
    "show birthday": show_birthday,
    "days to birthday": days_to_birthday,
    "exit": exit_command,
    "good bye": exit_command,
    "close": exit_command,
}


def parse_input(user_input):
    command, *args = user_input.split()
    command = command.lower().strip()

    try:
        handler = HANDLERS[command]
    except KeyError:
        if args:
            command = command + " " + args[0]
            args = args[1:]
        handler = HANDLERS.get(command, unknown_command)
    return handler, args


def main():
    while True:
        user_input = input("Please enter command and args: ")
        handler, args = parse_input(user_input)
        result = handler(*args)
        print(result)
        if handler == exit_command:
            break


if __name__ == "__main__":
    main()
