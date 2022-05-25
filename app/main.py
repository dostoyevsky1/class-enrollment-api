from fastapi import FastAPI, status, HTTPException, Response, Depends
from app import schemas, db
from typing import List

app = FastAPI()

@app.get('/')
async def root():
    return {'data':'hello world'}

@app.post('/semesters', status_code = status.HTTP_201_CREATED)
async def create_semester(semester: schemas.Semester):
    assert(isinstance(semester, schemas.Semester))
    try:
        created_semester_id = db.create_semester(**semester.dict())
        semester.sem_id = created_semester_id
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    return semester

@app.post('/students', status_code = status.HTTP_201_CREATED, response_model = schemas.StudentCreate)
async def create_student(student: schemas.StudentCreate):
    assert(isinstance(student, schemas.StudentCreate))
    try:
        created_student_id = db.create_student(**student.dict())
        student.student_id = created_student_id
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    return student

@app.put('/students/{student_id}', status_code = status.HTTP_202_ACCEPTED, response_model = schemas.StudentUpdate)
async def update_student(student_id: int, student_updated: schemas.StudentUpdate):
    try:
        student_updated.student_id = student_id
        db.update_student_fields(**student_updated.dict())
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    return student_updated

@app.post('/enrollments', status_code = status.HTTP_201_CREATED, response_model = schemas.Enrollment)
async def create_enrollment(enrollment: schemas.Enrollment):
    assert(isinstance(enrollment, schemas.Enrollment))
    try:
        db.create_enrollment(**enrollment.dict())
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    return enrollment

@app.get('/enrollments', response_model = List[schemas.ClassBase])
async def list_enrolled_classes(student_id: int, term: str, year: int):
    try:
        enrolled_classes = db.list_enrollments_for_semester(
            student_id = student_id,
            term = term,
            year = year
            )
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    enrolled_classes = [schemas.ClassBase(course_id = item[0], credits = item[1]) for item in enrolled_classes]
    if not enrolled_classes:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
        detail = f'Student {student_id} is not enrolled in any classes for {term}-{year}')
    return enrolled_classes

@app.get('/enrollments/audit', response_model = List[schemas.Class])
async def audit_student(student_id: int):
    try:
        enrolled_classes, fields = db.list_enrollments_for_student(
            student_id = student_id
            )
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    enrolled_classes = [list(zip(fields, item)) for item in enrolled_classes]
    enrolled_classes = [schemas.Class(**dict(item)) for item in enrolled_classes]
    if not enrolled_classes:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
        detail = f'Student {student_id} has not been enrolled in any classes')
    return enrolled_classes

@app.get('/students/{course_id}', response_model = List[schemas.StudentBase])
async def list_students_in_class(course_id: int, term: str, year: int):
    try:
        students, fields = db.list_students_in_class(
            course_id = course_id,
            term = term,
            year = year
            )
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    students = [list(zip(fields, item)) for item in students]
    students = [schemas.StudentBase(**dict(item)) for item in students]
    if not students:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
        detail = f'No students enrolled in this class')
    return students

@app.delete('/enrollments', status_code = status.HTTP_204_NO_CONTENT)
async def remove_student_from_class(enrollment: schemas.Enrollment):
    try:
        student_removed = db.remove_student_from_class(**enrollment.dict())
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    
    if not student_removed:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Student with id {enrollment.student_id} is not enrolled in course {enrollment.course_id} for {enrollment.term}-{enrollment.year}"
            )    
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.get('/classes/part-time', response_model = List[schemas.StudentClassLookup])
async def get_part_time_students_class_list(student_lookup: schemas.PartTimeLookup):
    try:
        students, fields = db.get_part_time_students_class_list(**student_lookup.dict())
    except:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)

    if not students:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
        detail = f'No students found that match criteria')

    students = [list(zip(fields, item)) for item in students]
    students = [schemas.StudentClassLookup(**dict(item)) for item in students]

    return students
