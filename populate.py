from config import db, app
from models import Course
import os
import csv

# If the Course class is updated, this file must be updated as well

def deleteAllCourses():
    Course.query.delete()
    db.session.commit()

def makeCourseFromRow(row, courseId):
    gradeDist = {"A+":0,"A":0,"A-":0,"B+":0,"B":0,"B-":0,
                "C+":0,"C":0,"C-":0,"D+":0,"D":0,"D-":0,
                "F":0,"W":0}
                #,"P":0,"NP":0,"I":0}
    termNumDict = {"Winter":0,"Spring":1,"Summer":2,"Fall":3}
    grades = ["A+","A","A-","B+","B","B-","C+","C","C-","D+","D","D-","F","W"] # Order in CSV. TODO: Add P/NP/I
    numStudents = 0
    
    sectionName = row[0]
    courseName = row[1]
    instructorName = row[2]
    secondaryInstructorName = row[3]
       
    for i in range(len(grades)): # Should be 14
        if row[i + 4] != "":
            gradeDist[grades[i]] = int(row[i + 4])
            numStudents += int(row[i + 4])
    term = row[18]
    termNum = termNumDict[term]
    year = int(row[19])
    # hasPlusMinus = row[20] == "0"
    return Course(courseId=courseId,
                  sectionName=sectionName,
                  courseName=courseName,
                  instructorName=instructorName,
                  secondaryInstructorName=secondaryInstructorName,
                  gradeDist=gradeDist,
                  term=term,
                  year=year,
                  numStudents=numStudents,
                  termNum=termNum
                  )

def deleteAndPopulate():
    with app.app_context():
        deleteAllCourses()
        currId = 1
        basePath = "./data"
        allEntries = os.listdir(basePath)
        allCsv = [entry for entry in allEntries if entry.endswith('.csv')]
        for fileName in allCsv:
            with open(os.path.join(basePath, fileName), 'r') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    # print(row)
                    if "SUBJECT_COURSE_SECTION" in row:
                        continue
                    newCourse = makeCourseFromRow(row, currId)
                    currId += 1
                    try:
                        db.session.add(newCourse)
                    except Exception as e:
                        print(f"Exception when adding course: {e}")
        try:
            db.session.commit()
        except Exception as e:
            print(f"Exception when committing added courses: {e}")
        print("Database reset and insertion complete.")

# if __name__ == "__main__":
#     populate()