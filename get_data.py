import pymysql
import csv
import datetime
import os
from config import host, user, password, db_name



try:
    connection = pymysql.connect(
        host = host,
        port = 3306,
        user = user,
        password = password,
        database = db_name,
        cursorclass = pymysql.cursors.DictCursor)
    def check_user(user_id):

        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            query_1 = f'SELECT user_id FROM user_1 WHERE user_id ={user_id}'
            cursor.execute(query_1)
            result = cursor.fetchone()
            if result != None:            #пользователь первой категории?
                category = 1
                connection.close()
                return category
            else:                          #пользователь второй категории?
                query_2 = f'SELECT user_id FROM user_2 WHERE user_id ={user_id}'
                cursor.execute(query_2)
                result = cursor.fetchone()
                if result != None:
                    category = 2
                    connection.close()
                    return category
                else:
                    category = 0
                    connection.close()
                    return category
    def insert_new_user(user_id):
       try:
            with connection.cursor() as cursor:
                connection.ping(reconnect=True)
                query_1 = f'INSERT INTO `user_2`(`user_id`, `number of requests`) VALUES ({user_id},0)'
                cursor.execute(query_1)
                connection.commit()
                cursor.close()
                return True
       except:
            return False

    def update_req(user_id):
        category = 0
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            query_1 = f"SELECT * FROM `user_1` WHERE user_id = {user_id}"
            cursor.execute(query_1)
            result = cursor.fetchall()
            print('user_1', result)
            if len(result) != 0:
                category = 1
            else:
                connection.ping(reconnect=True)
                query_2 = f"SELECT * FROM `user_2` WHERE user_id = {user_id}"
                cursor.execute(query_2)
                result = cursor.fetchall()
                print('user_2', result)
                if len(result) != 0:
                    category = 2

                print('category is', category)
            if category == 1:
                connection.ping(reconnect=True)
                query_1 = f"UPDATE `user_1` SET `number of requests`= `number of requests` + 1 WHERE `user_id` = {user_id} "
                cursor.execute(query_1)
                connection.commit()
                cursor.close()
                return True
            
            elif category == 2:
                connection.ping(reconnect=True)
                query_2 = f"UPDATE `user_2` SET `number of requests`= `number of requests` + 1 WHERE `user_id` = {user_id} "
                cursor.execute(query_2)
                connection.commit()
                cursor.close()
                return True


    def get_general_static():
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            query_1 = f'SELECT user_id, SUM(`number of requests`) FROM users_statics GROUP BY user_id'
            cursor.execute(query_1)
            result = cursor.fetchall()
            print(result)
            if len(result) != 0:
                lst_keys = []
                dict_keys = result[0].keys()

                for i in dict_keys:
                    lst_keys.append(i)
                with open('data.csv', 'w') as file:
                    writer = csv.writer(file)
                    writer.writerow(

                        lst_keys
                    )
                for j in range(len(result)):
                    lst_values = []
                    for k in result[j].values():
                        lst_values.append(k)
                    with open('data.csv', 'a') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            lst_values
                        )
                return True
            else:
                return False







    def get_static_today():

        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            current_date = datetime.date.today()
            day = current_date.day
            month = current_date.month
            year = current_date.year
            print(day, month, year)
            query_1 = f'SELECT * FROM `users_statics` WHERE day = {day} AND month = {month} AND year = {year} ORDER BY "number of requests" DESC'
            cursor.execute(query_1)
            result = cursor.fetchall()
            cursor.close()

            if len(result) != 0:
                lst_keys = []
                dict_keys = result[0].keys()

                for i in dict_keys:
                    lst_keys.append(i)
                with open('data.csv', 'w') as file:
                    writer = csv.writer(file)
                    writer.writerow(

                        lst_keys
                    )
                for j in range(len(result)):
                    lst_values = []
                    for k in result[j].values():
                        lst_values.append(k)
                    with open('data.csv', 'a') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            lst_values
                        )
                return True
            else:
                return False


    def get_static_week():
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            current_date = datetime.date.today()
            day = current_date.day
            month = current_date.month
            year = current_date.year
            one_week_ago = current_date - datetime.timedelta(days=7)
            day_last_week = one_week_ago.day
            month_last_week = one_week_ago.month
            year_last_week = one_week_ago.year
            if year != year_last_week:
                query_1 = f'SELECT * FROM `users_statics` WHERE day >= {day_last_week} AND month = {month_last_week} AND year = {year_last_week} OR day <= {day} ' \
                          f'AND month = {month} AND year = {year} ORDER BY month DESC, day DESC'
                cursor.execute(query_1)

                result = cursor.fetchall()
                cursor.close()
            elif year == year_last_week:
                query_1 = f'SELECT * FROM `users_statics` WHERE day >= {day_last_week} and month = {month_last_week} AND year = {year} OR day <= {day} ' \
                          f'AND month = {month} AND year = {year} ORDER BY month DESC, day DESC'
                cursor.execute(query_1)

                result = cursor.fetchall()
                cursor.close()

            if len(result) != 0:
                lst_keys = []
                dict_keys = result[0].keys()
                for i in dict_keys:
                    lst_keys.append(i)
                with open('data.csv', 'w') as file:
                    writer = csv.writer(file)
                    writer.writerow(

                        lst_keys
                    )
                for j in range(len(result)):
                    lst_values = []
                    for k in result[j].values():
                        lst_values.append(k)
                    with open('data.csv', 'a') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            lst_values
                        )

                return True
            else:
                return False

    def get_static_month():
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            current_date = datetime.date.today()
            day = current_date.day
            month = current_date.month
            year = current_date.year
            one_month_ago = current_date - datetime.timedelta(days=31)
            day_last_month = one_month_ago.day
            month_last_month = one_month_ago.month
            year_last_month = one_month_ago.year
            if year != year_last_month:
                query_1 = f'SELECT * FROM `users_statics` WHERE day >= {day_last_month} AND month = {month_last_month} AND year = {year_last_month} OR day <= {day} ' \
                          f'AND month = {month} AND year = {year} ORDER BY month DESC, day DESC'
                cursor.execute(query_1)

                result = cursor.fetchall()
                cursor.close()
            elif year == year_last_month:
                query_1 = f'SELECT * FROM `users_statics` WHERE day >= {day_last_month} AND month = {month_last_month} AND year = {year} OR day <= {day} ' \
                          f'AND month = {month} AND year = {year} ORDER BY month DESC, day DESC'
                cursor.execute(query_1)

                result = cursor.fetchall()
                cursor.close()

            if len(result) != 0:
                lst_keys = []
                dict_keys = result[0].keys()
                for i in dict_keys:
                    lst_keys.append(i)
                with open('data.csv', 'w') as file:
                    writer = csv.writer(file)
                    writer.writerow(

                        lst_keys
                    )
                for j in range(len(result)):
                    lst_values = []
                    for k in result[j].values():
                        lst_values.append(k)
                    with open('data.csv', 'a') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            lst_values
                        )

                return True
            else:
                return False

    def update_general_static(user_id):
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            current_date = datetime.date.today()
            day = current_date.day
            month = current_date.month
            year = current_date.year
            query_1 = f'SELECT * FROM `users_statics` WHERE day = {day} AND month = {month} AND year = {year} AND user_id = {user_id}'
            cursor.execute(query_1)
            result = cursor.fetchall()
            if len(result) != 0:
                query_2 = f'UPDATE `users_statics` SET `number of requests`= `number of requests` + 1 ' \
                          f'WHERE user_id = {user_id} AND day = {day} AND month = {month} AND year = {year}'
                cursor.execute(query_2)
                connection.commit()
                cursor.close()
            elif len(result) == 0:
                query_3 = f'INSERT INTO `users_statics`(`user_id`, `day`, `month`, `year`, `number of requests`) VALUES ({user_id},{day},{month},{year},{1})'
                cursor.execute(query_3)
                connection.commit()
                cursor.close()




    def allow_not_allow_processing():
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            query_1 = f'SELECT * FROM `user_1`'
            cursor.execute(query_1)
            result = cursor.fetchall()
            print(len(result))
            if len(result) != 0:
                query_2 = f'SELECT * FROM `user_1` WHERE processing = "NO" '
                cursor.execute(query_2)
                temp = cursor.fetchall()
                cursor.close()
                print(temp)
                if len(temp) == 0:
                    return True
                elif len(temp) != 0:

                    return False

    def update_not_allow(user_id):
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            query_1 = f'SELECT * FROM `user_1`'
            cursor.execute(query_1)
            result = cursor.fetchall()
            if len(result) != 0:
                query_2 = f'UPDATE `user_1` SET `processing`= "NO" WHERE user_id = {user_id} '
                cursor.execute(query_2)
                connection.commit()
                cursor.close()

    def update_allow(user_id):
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            query_1 = f'SELECT * FROM `user_1`'
            cursor.execute(query_1)
            result = cursor.fetchall()
            if len(result) != 0:
                query_2 = f'UPDATE `user_1` SET `processing`= "YES" WHERE user_id = {user_id} '
                cursor.execute(query_2)
                connection.commit()
                cursor.close()

    def delete_user(user_id):
        try:
            with connection.cursor() as cursor:
                connection.ping(reconnect=True)
                query_check = f'SELECT `user_id`  FROM `user_2` WHERE user_id = {user_id} '
                cursor.execute(query_check)
                result = cursor.fetchone()
                if result != None:
                    query_1 = f'DELETE FROM `user_2` WHERE user_id = {user_id}'
                    cursor.execute(query_1)
                    connection.commit()
                    cursor.close()
                    return True
                else:
                    return False
        except:
            return False
    print('Соединение установлено')
except Exception as ex:
    print('Подключение не удалось установить')
    print(ex)
