from core.settings import ALL_DB_COLUMNS


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")


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
