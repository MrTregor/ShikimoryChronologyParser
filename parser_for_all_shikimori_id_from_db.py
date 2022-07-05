import pymysql
import config
from shikimory_parser_by_id import get_chronology_by_id

con = pymysql.connect(host=config.host, user=config.user, password=config.password, db=config.db,
                      charset=config.charset, autocommit=config.autocommit)
shikimori_ids = []
with con:
    cur = con.cursor()

    # 100000 наибольший shikimori id, нужен чтобы можно было продолжить остановленный парсинг
    cur.execute("SELECT `shikimori_id` FROM `animes` WHERE `shikimori_id`<100 ORDER BY `shikimori_id` DESC")
    shikimori_ids_from_db = cur.fetchall()

    for row in shikimori_ids_from_db:
        shikimori_ids.append(int("{0} ".format(row[0])))
    # По умолчанию значение 1 отвечает за chronology id
    row_id = 1584
    for anime_id in shikimori_ids:
        if anime_id == 38938:
            # Аниме: Этот глупый свин не понимает мечту девочки-зайки: Спецвыпуски
            # И shikimori о нём почему-то не знает
            continue

        # Если уже существует в базе
        cur = con.cursor()
        cur.execute(
            f"SELECT `chronology_id` FROM `chronology` WHERE `anime_chronology_data` LIKE '%\"shikimori_id\": {anime_id},%' ")
        shikimori_ids_from_db = cur.fetchall()

        if len(shikimori_ids_from_db) != 0:
            # То записываем имеющийся chronology id
            print(anime_id, "Уже имеется")
            exist_row_id = int("{0} ".format(shikimori_ids_from_db[0][0]))
            cur.execute(f"UPDATE `animes` SET `chronology_anime_id`='{exist_row_id}' WHERE `shikimori_id`={anime_id}")
        else:
            # Иначе парсим новое аниме
            anime_data = get_chronology_by_id(anime_id)
            print(anime_id, anime_data)
            string_data = str(anime_data).replace('\'', '\"')
            if string_data != "False":
                sql = f"INSERT INTO `chronology`(`chronology_id`, `anime_chronology_data`) VALUES ({row_id}, '{string_data}')"
                try:
                    # Добавляем новую хронологию и записываем её в таблицу с аниме
                    cur.execute(sql)
                    cur.execute(
                        f"UPDATE `animes` SET `chronology_anime_id`='{row_id}' WHERE `shikimori_id`={anime_id}")
                    row_id += 1
                except pymysql.err.IntegrityError:
                    pass
