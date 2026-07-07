from langchain_core.tools import tool
from retriever import retrieve
import mysql.connector
from langchain_google_genai import ChatGoogleGenerativeAI





llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="GOOGLE_API_KEY",
    temperature=0
)




def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password",
        database="college_feedback"
    )

def save_message(session_id, role, message):
    
    conn = get_connection()

    cursor = conn.cursor()

    sql = """
    INSERT INTO conversation_history
    (session_id, role, message)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (session_id, role, message))

    conn.commit()

    conn.close()
    
def load_history(session_id):

    conn = get_connection()

    cursor = conn.cursor()

    sql = """
    SELECT role, message
    FROM conversation_history
    WHERE session_id = %s
    ORDER BY id ASC
    """

    cursor.execute(sql, (session_id,))

    history = cursor.fetchall()

    conn.close()

    return history


    


@tool
def feedback_search(question: str) -> str:
    """
    Search the student feedback vector database.

    Use this tool whenever the user asks about:
    - Student feedback
    - Student comments
    - Reviews
    - Opinions
    - Teaching quality
    - What students say about a lecturer
    - Feedback for a lecturer
    - Positive feedback
    - Negative feedback

    Input:
        A natural language question.

    Returns:
        Relevant feedback retrieved from the vector database.
    """

    print("=" * 60)
    print("📚 FEEDBACK SEARCH TOOL")
    print("Question:", question)
    print("=" * 60)

    try:
        docs = retrieve(question)

        if not docs:
            return "No relevant feedback found."

        feedback = []

        for i, doc in enumerate(docs, start=1):
            feedback.append(
                f"""
Feedback {i}

{doc.page_content}
"""
            )

        return "\n" + ("-" * 60 + "\n").join(feedback)

    except Exception as e:
        return f"Feedback search failed: {str(e)}"



@tool
def sql_query(question: str) -> str:
    """
    Query the College Feedback SQL database.

    Use this tool whenever the user asks about:
    - Average rating
    - Highest/Lowest rating
    - Pass percentage
    - Fail percentage
    - Attendance
    - Student marks
    - Lecturer information
    - Subject information
    - Qualification
    - Experience
    - Semester
    - Academic year
    """

    print("=" * 70)
    print("🗄 SQL TOOL")
    print("Question:", question)
    print("=" * 70)

    try:

        conn=get_connection()

        cursor = conn.cursor()

        prompt = f"""
You are an expert MySQL SQL query generator.
Convert the user's question into a single valid MySQL SELECT query.

Database: college_feedback
Table: feedback

Schema:
student_id, academic_year, semester, section, lecture_id, lecture_name,
lecture_department, lecture_qualification, lecture_experience_years,
lecture_type, subject_code, subject_name, attendance_percentage,
rating_date, student_marks, pass_fail, student_rating, student_comment

Column meanings:
lecture_name -> Lecturer name
subject_name -> Subject name
student_rating -> Rating (1-5)
student_comment -> Student feedback/comments
attendance_percentage -> Attendance percentage
student_marks -> Student marks
pass_fail -> 'Pass' or 'Fail'
lecture_department -> Lecturer department
lecture_qualification -> Lecturer qualification
lecture_experience_years -> Experience in years

STRICT RULES
1. Use ONLY the feedback table. Never invent tables/columns. No JOIN.
2. Only SELECT statements. Never INSERT/UPDATE/DELETE/DROP/ALTER/CREATE.
3. Always include FROM feedback.
4. Output ONLY the raw SQL query — no markdown fences, no explanation,
   no leading/trailing text, no trailing semicolon.
5. Use DISTINCT with student_id whenever counting students, to avoid
   double-counting across rows (a student can have multiple feedback rows).

INTENT → SQL PATTERN

A) "How many students <condition>" -> row/count question, NOT percentage
   SELECT COUNT(DISTINCT student_id) FROM feedback WHERE <condition>

B) "Average <metric>" (rating/marks/attendance), overall
   SELECT ROUND(AVG(<column>),2) FROM feedback WHERE <filters>

C) "Average <metric> per/by <dimension>" (lecturer/subject/department/etc.)
   -> Requires GROUP BY. Include the dimension column in SELECT.
   SELECT <dimension_column>, ROUND(AVG(<column>),2) AS avg_value
   FROM feedback WHERE <filters>
   GROUP BY <dimension_column>

D) "Highest/Maximum <value>" as a single number (e.g. highest marks scored)
   SELECT MAX(<column>) FROM feedback WHERE <filters>

E) "Which <entity> has the highest/lowest/top <metric>"
   -> This is NOT a MAX()/MIN() scalar. It requires grouping + ranking.
   SELECT <entity_column>, ROUND(AVG(<metric>),2) AS avg_value
   FROM feedback WHERE <filters>
   GROUP BY <entity_column>
   ORDER BY avg_value DESC   -- DESC for highest/top, ASC for lowest
   LIMIT 1                   -- or LIMIT N if "top N" is asked

F) "Percentage/Percent/%"
   SELECT ROUND(
     COUNT(DISTINCT CASE WHEN <condition> THEN student_id END) * 100.0
     / COUNT(DISTINCT student_id), 2) AS percentage
   FROM feedback WHERE <base_filters>

G) "List/Show/Give me <rows>" (comments, names, records — no aggregation)
   SELECT DISTINCT <relevant_columns> FROM feedback WHERE <filters>
   -- Add ORDER BY rating_date DESC if recency is implied.
   -- Add LIMIT N if a specific count of rows is asked ("show 5 comments").

H) "Count of <rows>" not tied to students (e.g. "how many feedback entries")
   SELECT COUNT(*) FROM feedback WHERE <filters>

FILTERING RULES
- Passed students: WHERE pass_fail = 'Pass'
- Failed students: WHERE pass_fail = 'Fail'
- Lecturer name: WHERE lecture_name = '<lecturer_name>'
- Subject name: WHERE subject_name = '<subject_name>'
- Department: WHERE lecture_department = '<department>'
- Qualification: WHERE lecture_qualification = '<qualification>'
- Combine multiple filters with AND as needed.

DISAMBIGUATION
- "How many" -> COUNT, never a percentage.
- "Percentage"/"percent"/"%" -> percentage formula, never plain COUNT.
- "Maximum/highest <numeric value>" alone -> MAX() (pattern D).
- "Which/who has the highest/most/best <metric>" -> GROUP BY + ORDER BY + LIMIT (pattern E), NOT MAX().
- If a question implies grouping by an entity (per lecturer, per subject,
  per department, per semester, per year), you MUST GROUP BY that column
  and include it in the SELECT list.

FEW-SHOT EXAMPLES

Q: How many students passed?
SQL: SELECT COUNT(DISTINCT student_id) FROM feedback WHERE pass_fail = 'Pass'

Q: How many students failed in the CSE department?
SQL: SELECT COUNT(DISTINCT student_id) FROM feedback WHERE pass_fail = 'Fail' AND lecture_department = 'CSE'

Q: What is the pass percentage?
SQL: SELECT ROUND(COUNT(DISTINCT CASE WHEN pass_fail = 'Pass' THEN student_id END) * 100.0 / COUNT(DISTINCT student_id), 2) AS percentage FROM feedback

Q: What is the average rating for lecturer John Smith?
SQL: SELECT ROUND(AVG(student_rating),2) FROM feedback WHERE lecture_name = 'John Smith'

Q: What is the average rating for each lecturer?
SQL: SELECT lecture_name, ROUND(AVG(student_rating),2) AS avg_rating FROM feedback GROUP BY lecture_name

Q: Which lecturer has the highest average rating?
SQL: SELECT lecture_name, ROUND(AVG(student_rating),2) AS avg_rating FROM feedback GROUP BY lecture_name ORDER BY avg_rating DESC LIMIT 1

Q: What are the top 3 subjects by average marks?
SQL: SELECT subject_name, ROUND(AVG(student_marks),2) AS avg_marks FROM feedback GROUP BY subject_name ORDER BY avg_marks DESC LIMIT 3

Q: What is the highest mark scored in Physics?
SQL: SELECT MAX(student_marks) FROM feedback WHERE subject_name = 'Physics'

Q: Show me comments from students who failed.
SQL: SELECT DISTINCT student_id, student_comment FROM feedback WHERE pass_fail = 'Fail'

Q: How many feedback entries are there for the Computer Science department?
SQL: SELECT COUNT(*) FROM feedback WHERE lecture_department = 'Computer Science'

Q: What is the average attendance percentage of students who failed?
SQL: SELECT ROUND(AVG(attendance_percentage),2) FROM feedback WHERE pass_fail = 'Fail'

User Question:
{question}
SQL:
"""

        sql = llm.invoke(prompt).content.strip()

        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

        print("\nGenerated SQL:")
        print(sql)

        if not sql.lower().startswith("select"):
            conn.close()
            return f"Invalid SQL generated:\n{sql}"

        cursor.execute(sql)

        rows = cursor.fetchall()

        conn.close()

        if not rows:
            return "No matching records found."

        # Single value
        if len(rows) == 1 and len(rows[0]) == 1:

            value = rows[0][0]

            if value is None:
                return "No matching records found."

            return str(value)

        # Multiple rows
        result = ""

        for row in rows:
            result += " | ".join(str(col) for col in row)
            result += "\n"

        return result

    except Exception as e:
        return f"Database Error: {str(e)}"


@tool
def sentiment_analysis(lecturer_name: str) -> str:
    
    
    """
    Summarize student feedback for a lecturer.

    Use this tool whenever the user asks:

    - Summarize feedback
    - Overall feedback
    - Strengths
    - Weaknesses
    - Student opinion
    - Teaching quality
    - Review summary
    """
    
    print(">>> SENTIMENT TOOL EXECUTED <<<")
    

    print("=" * 70)
    print("📊 SENTIMENT ANALYSIS TOOL")
    print("Lecturer:", lecturer_name)
    print("=" * 70)

    docs = retrieve(lecturer_name)

    if not docs:
        return f"No feedback found for '{lecturer_name}'."

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are an education analyst.

Analyze the following student feedback for the lecturer.

Lecturer:
{lecturer_name}

Feedback:
{context}

Your task:

1. Overall Opinion (2-3 sentences)

2. Strengths
- Bullet points

3. Weaknesses
- Bullet points

4. Student Satisfaction
Mention whether students are:
- Very Satisfied
- Satisfied
- Neutral
- Dissatisfied

5. Suggestions for Improvement

6. Final Conclusion

Keep the response concise, professional, and based ONLY on the feedback provided.
Do not invent information.
"""

    try:
        response = llm.invoke(prompt)

        if hasattr(response, "content"):
            return response.content

        return str(response)

    except Exception as e:
        return f"Sentiment analysis failed: {str(e)}"

@tool
def compare_lecturers(lecturer1:str, lecturer2:str)->str:

    """
    Compare two lecturers using student feedback.
    """
    
    print(">>> COMPARE TOOL EXECUTED <<<")
    

    docs1 = retrieve(lecturer1)
    docs2 = retrieve(lecturer2)

    if not docs1 or not docs2:
        return "Feedback not found."

    feedback1 = "\n".join(doc.page_content for doc in docs1)
    feedback2 = "\n".join(doc.page_content for doc in docs2)

    prompt = f"""
Compare these lecturers.

Lecturer:
{lecturer1}

Feedback:
{feedback1}



Lecturer:
{lecturer2}

Feedback:
{feedback2}

Compare:

- Strengths
- Weaknesses
- Teaching style
- Overall recommendation
"""

    return llm.invoke(prompt).content

@tool
def recommend_lecturer(subject:str)->str:
    """
    Recommend the best lecturer for a subject.
    """

    docs = retrieve(subject)

    if not docs:
        return "No feedback found."

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Subject:
{subject}

Feedback:

{context}

Recommend the best lecturer.

Mention:

- Best lecturer
- Why
- Strengths
- Weaknesses

Keep it concise.
"""

    return llm.invoke(prompt).content


@tool
def subject_summary(subject:str)->str:
    """
    Summarize feedback for a subject.
    """

    docs = retrieve(subject)

    if not docs:
        return "No feedback found."

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Subject:
{subject}

Feedback:

{context}

Summarize:

- Overall opinion
- Positive points
- Common complaints
- Final summary
"""

    return llm.invoke(prompt).content