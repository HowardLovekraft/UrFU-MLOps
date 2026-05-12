import psycopg

from src.schemas import RecordSchema, PredictionSchema


def create_table():
    with (
        psycopg.connect("host=db dbname=postgres user=postgres password=1337") as conn,
        conn.cursor() as cur
    ):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                period TEXT,
                subject TEXT,
                co2_ppm DOUBLE PRECISION,
                pm25_ugm3 DOUBLE PRECISION,
                temperature_c DOUBLE PRECISION,
                humidity_pct DOUBLE PRECISION,
                reaction_time_ms INTEGER,
                focus_rating DOUBLE PRECISION,
                error_rate DOUBLE PRECISION,
                heart_rate_bpm INTEGER,
                cognitive_impairment DOUBLE PRECISION,
                air_quality INTEGER,
                performance_index INTEGER
            )
        """)


def get_record(record: RecordSchema):
    with (
        psycopg.connect("host=db dbname=postgres user=postgres password=1337") as conn,
        conn.cursor() as cur
    ):
        cur.execute("""
            SELECT performance_index
              FROM predictions
             WHERE period = %s
               AND subject = %s
               AND co2_ppm = %s
               AND pm25_ugm3 = %s
               AND temperature_c = %s
               AND humidity_pct = %s
               AND reaction_time_ms = %s
               AND focus_rating = %s
               AND error_rate = %s
               AND heart_rate_bpm = %s
               AND cognitive_impairment = %s
               AND air_quality = %s
        """, tuple(record.model_dump().values()))
        result: tuple[int] | None = cur.fetchone()
        if result is None:
            return None
        return result[0]


def add_record(record: RecordSchema, performance_index: int) -> None:
    with (
        psycopg.connect("host=db dbname=postgres user=postgres password=1337") as conn,
        conn.cursor() as cur
    ):
        cur.execute(
            """
            INSERT INTO predictions
            VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            tuple(record.model_dump().values()) + (performance_index,)
        )
        conn.commit()
