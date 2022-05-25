from app import config
import psycopg2 as ps
from tenacity import retry, wait_exponential

PS_CONNECTION_STRING = f"dbname={config.POSTGRES_DB} user={config.POSTGRES_USER} password={config.POSTGRES_PASSWORD} host={config.POSTGRES_HOST} port={config.POSTGRES_PORT}"

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
def _init_db():
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS course (
                    course_id serial not null,
                    credits int not null,

                    primary key (course_id, credits)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS semester (
                    sem_id serial not null,
                    term varchar(6) not null,
                    year int not null,

                    primary key (year, term)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS class (
                    course_id int not null,
                    credits int not null,
                    term varchar(6) not null,
                    year int not null,

                    primary key (course_id, year, term),
                    foreign key (course_id, credits) references course (course_id, credits),
                    foreign key (term, year) references semester (term, year) 
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS student (
                    student_id serial not null,
                    phone_number varchar(10) not null,
                    first_name varchar(50) not null,
                    last_name varchar(50) not null,
                    nationality varchar(50) not null,
                    gender varchar(6) not null,

                    primary key (student_id)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS enrollment (
                    student_id int not null,
                    course_id int not null,
                    term varchar(6) not null,
                    year int not null,
                
                    primary key (student_id, course_id, term, year),
                    foreign key (student_id) references student (student_id),
                    foreign key (course_id, term, year) references class (course_id, term, year)
                    );
                """)
    except Exception as e:
        raise e

def add_test_data():
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                insert into course values (DEFAULT, 3);
                insert into course values (DEFAULT, 4);

                insert into semester values (DEFAULT, 'fall', 2022);
                insert into semester values (DEFAULT, 'spring', 2022);
                insert into semester values (DEFAULT, 'fall', 2021);
                insert into semester values (DEFAULT, 'spring', 2021);

                insert into class values (1, 3, 'fall', 2022);
                insert into class values (2, 4, 'fall', 2022);
                insert into class values (1, 3, 'spring', 2021);
                insert into class values (2, 4, 'spring', 2021);

                insert into student values (DEFAULT, '123123', 'mike', 'drozd', 'usa', 'male');
                insert into student values (DEFAULT, '098098', 'ash', 'kinsey', 'usa', 'female');

                insert into enrollment values (1, 1, 'fall', 2022);
                insert into enrollment values (1, 2, 'fall', 2022);
                insert into enrollment values (2, 1, 'spring', 2021);
                insert into enrollment values (2, 2, 'fall', 2022);
                """)
                # cur.execute("""
                #     INSERT INTO reviews (review_label, description, date) VALUES (%s, %s, %s)
                #     """,
                #     (review_label, description, date)
                #     )
    except Exception as e:
        raise e
    
def create_student(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO student VALUES (DEFAULT, %s, %s, %s, %s, %s) RETURNING student_id;
                """,(
                    kwargs.get('phone_number'),
                    kwargs.get('first_name'),
                    kwargs.get('last_name'),
                    kwargs.get('nationality'),
                    kwargs.get('gender'), 
                    )
                )
                return_val = cur.fetchone()[0]
                return return_val
    except Exception as e:
        raise e

def update_student_fields(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                student_id = kwargs.pop('student_id')
                for key, value in kwargs.items():
                    if value:
                        cur.execute(f"""
                            UPDATE student SET {key} = '{value}' WHERE student_id = {student_id};
                        """       
                        )
    except Exception as e:
        raise e

def create_semester(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO semester VALUES (DEFAULT, %s, %s) RETURNING sem_id;
                """,(
                    kwargs.get('term'),
                    kwargs.get('year'),
                    )
                )
                return_val = cur.fetchone()[0]
                return return_val
    except Exception as e:
        raise e

def create_enrollment(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO enrollment VALUES (%s, %s, %s, %s);
                """,(
                    kwargs.get('student_id'),
                    kwargs.get('course_id'),
                    kwargs.get('term'),
                    kwargs.get('year'),
                    )
                )
    except Exception as e:
        raise e

def list_enrollments_for_semester(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.* 
                    FROM enrollment e 
                    INNER JOIN 
                    course c 
                    ON e.course_id = c.course_id 
                    WHERE e.student_id = %s AND e.term = %s AND e.year = %s;
                """,(
                    kwargs.get('student_id'),
                    kwargs.get('term'),
                    kwargs.get('year'),
                    )
                )
                return_val = cur.fetchall()
                return return_val
    except Exception as e:
        raise e

def list_enrollments_for_student(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.* FROM enrollment e 
                    LEFT JOIN class c 
                    ON e.course_id = c.course_id AND e.term = c.term AND e.year = c.year 
                    WHERE e.student_id = %s;
                """,(
                    kwargs.get('student_id'),
                    )
                )
                return_val = cur.fetchall()
                return_fields = [col[0] for col in cur.description]
                return return_val, return_fields
    except Exception as e:
        raise e

def list_students_in_class(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT student_id FROM enrollment WHERE course_id = %s AND term = %s AND year = %s;
                """,(
                    kwargs.get('course_id'),
                    kwargs.get('term'),
                    kwargs.get('year'),
                    )
                )
                return_val = cur.fetchall()
                return_fields = [col[0] for col in cur.description]
                return return_val, return_fields
    except Exception as e:
        raise e

def remove_student_from_class(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM enrollment 
                    WHERE student_id = %s AND course_id = %s AND term = %s AND year = %s
                    RETURNING student_id;
                """,(
                    kwargs.get('student_id'),
                    kwargs.get('course_id'),
                    kwargs.get('term'),
                    kwargs.get('year'),
                    )
                )
                return_val = cur.fetchall()
                return return_val
    except Exception as e:
        raise e

def get_part_time_students_class_list(**kwargs):
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                NULL = 'NULL'
                term = kwargs.get('term')
                year = kwargs.get('year')
                first_name_filter = kwargs.get('first_name_filter')
                if first_name_filter:
                    first_name_filter = f'{first_name_filter}%'
                last_name_filter = kwargs.get('last_name_filter')
                if last_name_filter:
                    last_name_filter = f'{last_name_filter}%'
                nationality_filter = kwargs.get('nationality_filter')
                gender_filter = kwargs.get('gender_filter')
                cur.execute("""
                    with parttimers as 
                    (
                        select student_id from enrollment e 
                        join class c on e.course_id = c.course_id and e.term = c.term and e.year = c.year 
                        where e.year = %s and e.term = %s
                        group by student_id 
                        having sum(credits) < 10
                    ),
                    filtered as 
                    (
                        select s.* from parttimers p 
                        join student s on p.student_id = s.student_id 
                        where (
                            first_name like coalesce(%s, first_name) 
                            or last_name like coalesce(%s, last_name)
                            ) 
                        and nationality = coalesce(%s, nationality) 
                        and gender = coalesce(%s, gender)
                    ),
                    student_class as 
                    (
                        select f.*, e.course_id, e.term, e.year from filtered f 
                        join enrollment e on f.student_id = e.student_id 
                        where term = %s and year = %s
                    )
                    select student_id, phone_number, first_name, last_name, nationality, gender, term, year, STRING_AGG(course_id::varchar, ', ') as course_list 
                    from student_class 
                    group by(student_id, phone_number, first_name, last_name, nationality, gender, term, year);
                """,(
                    year,
                    term,
                    first_name_filter,
                    last_name_filter,
                    nationality_filter,
                    gender_filter,
                    term,
                    year,
                )
                )
                return_val = cur.fetchall()
                return_fields = [col[0] for col in cur.description]
                return return_val, return_fields
    except Exception as e:
        raise e

def _drop_schema():
    try:
        with ps.connect(PS_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DROP SCHEMA public CASCADE;
                """
                )
    except Exception as e:
        raise e

_init_db()
try:
    add_test_data()
except:
    pass