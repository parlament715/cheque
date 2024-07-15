text_template = "\
  <U><I>Вот как будет выглядеть карточка</I></U>\
  \n☕️ <B>{company_name}.</B>\
  \n👏 Карточку внес @{user_name_telegram} 👏\
  \n🏛️ {address};\
  \n⌚️ {date_time};\
  \n🧾 Номер чека : {cheque_number};\
  \nФД {FD};\
  \nСмена {shift_number};\
  \nСреднее значение ФД/Смена = {FD_shift_number};\
  \nКомментарий : {Comment}."

text = "\
  ☕️ <B>{company_name}.</B>\
  \n👏 Карточку внес @{user_name_telegram} 👏\
  \n🏛️ {address};\
  \n⌚️ {date_time};\
  \n🧾 Номер чека : {cheque_number};\
  \nФД {FD};\
  \nСмена {shift_number};\
  \nСреднее значение ФД/Смена = {FD_shift_number};\
  \nКомментарий : {Comment}."


def format_text(text:str,data:dict):
  return text.format(company_name=data["company_name"].replace("<","").replace(">",""),
    user_name_telegram=data["user_name_telegram"].replace("<","").replace(">",""),
    address=data["address"].replace("<","").replace(">",""),
    date_time=data["date_time"].replace("<","").replace(">",""),
    cheque_number=data["cheque_number"],
    FD=data["FD"].replace("<","").replace(">",""),
    shift_number=data["shift_number"].replace("<","").replace(">",""),
    FD_shift_number=round(int(data["FD"])/int(data["shift_number"])),
    Comment = data["Comment"].replace("<","").replace(">",""))
### round(int(data["ФД"])/int(data["Смена №"]))
# print(text.format(company_name="Правда Кофе",user_name_telegram="@MaxSw",address="г. Москва, ул Тверская-Ямская 1-я, д 2, стр 1",date_time="17.05.2024 07:14",cheque_number=122,FD="88216",shift_number="569",FD_shift_number=round(int("88216")/int("569")),Comment = "---"))