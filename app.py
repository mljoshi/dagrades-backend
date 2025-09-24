from flask import request, jsonify
from config import app, db
from models import Course
from sqlalchemy import or_, and_
from populate import deleteAndPopulate
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT_NUM = int(os.environ.get('PORT', 8080))
COURSES_PER_PAGE = 9
SECTION_SPLITTER = ":"

def getGeneralCourseSection(sectionName):
    lastSplitterInd = sectionName.rfind(SECTION_SPLITTER)
    if lastSplitterInd == -1:
        return sectionName # lastSplitterInd not found in sectionName?
    else:
        return sectionName[:lastSplitterInd].strip(":. \n")

# Includes the current course
def getSimilarCoursesInTerm(course):
    sectionName = course.sectionName
    termNum = course.termNum
    year = course.year
    genSection = getGeneralCourseSection(sectionName)
    query = Course.query.filter(and_(Course.sectionName.ilike(f"{genSection}%"), Course.termNum == termNum, Course.year == year))
    courses = query.all()
    return courses

def getGradeAndStudentTotals(courses):
    # A+,A,A-,B+,B,B-,C+,C,C-,D+,D,D-,F,W
    # TODO: ,P,NP,I
    gradeTotalsDict = {"A+":0,"A":0,"A-":0,"B+":0,"B":0,"B-":0,
                "C+":0,"C":0,"C-":0,"D+":0,"D":0,"D-":0,
                "F":0,"W":0}
                #,"P":0,"NP":0,"I":0}
    studentTotal = 0
    for course in courses:
        for grade in gradeTotalsDict:
            if grade in course.gradeDist:
                gradeTotalsDict[grade] += course.gradeDist[grade]
        studentTotal += course.numStudents
    return [v for (k,v) in gradeTotalsDict.items()], studentTotal





@app.route("/api/courses/<int:courseId>", methods=["GET"])
def getCourse(courseId):
    if not courseId:
        return (
            jsonify({"message": "You must include a course ID."}),
            400,
            )
    # TODO: Add input checking on the id to ensure it is a number? Unless the <int: handles that
    course = Course.query.get(courseId)
    if not course:
        return (
            jsonify({"message": "Your course ID is invalid."}),
            400,
            )
    listData = course.toList()
    aggregatedGrades, aggregatedStudents = getGradeAndStudentTotals(getSimilarCoursesInTerm(course))
    return jsonify({"course": listData, "classSize": course.numStudents,"aggregatedGrades":aggregatedGrades, "totalStudents":aggregatedStudents})

@app.route("/api/courses", methods=["GET"])
def getCourses():
    data = request.args
    pageNum = data.get("page", type=int)
    searchStr = data.get("q")
    query = Course.query.order_by(Course.year.desc(), Course.termNum.desc())
    if not pageNum:
        return (
            jsonify({"message": "Your page number is invalid."}),
            400,
            )
    if searchStr:
       query = query.filter(or_(Course.courseName.ilike(f"%{searchStr}%"), Course.sectionName.ilike(f"%{searchStr}%"), Course.instructorName.ilike(f"%{searchStr}%")))
    totalItems = query.count()
    startInd = (pageNum - 1) * COURSES_PER_PAGE
    courses = query.offset(startInd).limit(COURSES_PER_PAGE).all()
    listData = [course.toList() for course in courses]
    return jsonify({"data": listData, "totalItems": totalItems})
# NOTE: totalItems is 0 in the original API if pg>pg_max

# Excludes the current course
@app.route("/api/similar-courses/<int:courseId>")
def getSimilarCourses(courseId):
    if not courseId:
        return (
            jsonify({"message": "You must include a course ID."}),
            400,
            )
    course = Course.query.get(courseId)
    if not course:
        return (
            jsonify({"message": "Your course ID is invalid."}),
            400,
            )
    genSection = getGeneralCourseSection(course.sectionName)
    # FIXME: inconsistent . in the courseSection results in a separation of the recent from the old data
    query = Course.query.order_by(Course.year.desc(), Course.termNum.desc()).filter(and_(Course.sectionName.ilike(f"%{genSection}%"), Course.courseId != course.courseId))
    courses = query.all()
    listData = [cour.toList() for cour in courses]
    return jsonify(listData)
    

with app.app_context():
    db.create_all()

deleteAndPopulate()

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, port=PORT_NUM)