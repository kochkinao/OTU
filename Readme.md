# Парсер PDF расписания
1) В папку timetables положить PDF файл с расписанием занятий.
2) Вызвать функцию parse_timetables из одноимённого скрипта. (В качестве аргументов можно указать путь выходного файла CSV)
3) Из файла csv_manager.py импортировать PDFScheduleLoader
4) Создать объект loader = PDFScheduleLoader(url базы данных)
5) Для получения данных о расписании группы за день/неделю использовать методы get_daily_schedule и get_weekly_schedule соответственно.
6) При обновлении расписания вызвать loader.read_schedule_file()
