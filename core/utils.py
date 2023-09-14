from core.settings import ALL_DB_COLUMNS


def employee_card_message(employee):
    ''' Функция строит текст переданого ей  элемента из бд.
        возвращает текст и есть ли у него аватар
    '''
    employee_card = []
    avatar_detected = False
    for i in range(len(employee)):
        col_name = ALL_DB_COLUMNS[i].upper()
        val = employee[i]
        if col_name == 'AVATAR':
            if val is not None:
                avatar_detected = True
            continue
        if val is None:
            val = 'Пусто'
        employee_card.append(f'{col_name} - {val}')
    return '\n'.join(employee_card), avatar_detected


def form_list_message(list_of_users):
    print(list_of_users)
    if len(list_of_users) == 0:
        return "Работники, не были найдены("
    message = f'СПИСОК РАБОТНИКОВ, ПОДХОДЯЩИХ ПОД УСЛОВИЕ:\nID|ИМЯ|ОТЧЕСТВО|ФАМИЛИЯ|ДОЛЖНОСТЬ|ПРОЕКТ|ВРЕМЯ\n'
    ans = []
    for i in list_of_users:
        ans.append(' | '.join(map(str, i)))
    return message + '\n'.join(ans)
