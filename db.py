import pymysql
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import random
import calendar

# MySQL 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'dbhomework',
    'charset': 'utf8mb4'
}

# 连接到数据库
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("成功连接到数据库")
            return connection
    except Error as e:
        print(f"连接数据库时发生错误: {e}")
        return None

connection = connect_to_database()
# 创建表
def create_tables(connection):
    try:
        cursor = connection.cursor()

        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)

        # 锻炼时间统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ExerciseTime (
                id INT,
                username VARCHAR(255),
                time DATETIME,
                exercise_duration INT,
                FOREIGN KEY (id) REFERENCES Users(id)
            )
        """)

        # 课程报名表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CourseRegistration (
                id INT,
                username VARCHAR(255),
                time DATETIME,
                course VARCHAR(255),
                FOREIGN KEY (id) REFERENCES Users(id)
            )
        """)

        # 课程统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Course (
                id INT,
                course VARCHAR(255),
                discription TEXT,
                duration INT,
                interval_time INT,
                total_people INT,
                FOREIGN KEY (id) REFERENCES Users(id)
            )
        """)

        # 训练规划表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TrainingPlan (
                id INT,
                username VARCHAR(255),
                time DATETIME,
                course VARCHAR(255),
                exercise_duration INT,
                FOREIGN KEY (id) REFERENCES Users(id)
            )
        """)

        # print("表创建成功")
        cursor.close()
    except Error as e:
        print(f"创建表时发生错误: {e}")
def create_indexes(connection):
    try:
        cursor = connection.cursor()
        # 创建用户索引
        cursor.execute("CREATE INDEX idx_username ON ExerciseTime(username)")
        # 创建训练时长索引
        cursor.execute("CREATE INDEX idx_exercise_duration ON ExerciseTime(exercise_duration)")
        # 创建训练时间点索引
        cursor.execute("CREATE INDEX idx_time ON ExerciseTime(time)")
        # 创建 username 索引
        cursor.execute("CREATE INDEX idx_username ON CourseRegistration(username)")
        # 创建 course 索引
        cursor.execute("CREATE INDEX idx_course ON CourseRegistration(course)")
        cursor.close()
    except Error as e:
        print(f"创建索引时发生错误: {e}")

def create_triggers(connection):
    try:
        cursor = connection.cursor()
        # 触发器 1: 当用户订阅课程时，课程的人数增加
        cursor.execute("""
            CREATE TRIGGER increment_course_people
            AFTER INSERT ON CourseRegistration
            FOR EACH ROW
            BEGIN
                UPDATE Course
                SET total_people = total_people + 1
                WHERE course = NEW.course;
            END;
        """)
        # 触发器 2: 当用户订阅课程时，自动添加训练计划
        cursor.execute("""
            CREATE TRIGGER add_training_plan
            AFTER INSERT ON CourseRegistration
            FOR EACH ROW
            BEGIN
                DECLARE next_time DATETIME;
                DECLARE interval_days INT;
                DECLARE course_duration INT;

                -- 获取课程的 duration 和 interval_time
                SELECT duration, interval_time INTO course_duration, interval_days
                FROM Course
                WHERE course = NEW.course;

                -- 初始化 next_time 为 NEW.time
                SET next_time = NEW.time;

                -- 循环检查并插入/更新 TrainingPlan 表中的记录
                WHILE next_time <= DATE_ADD(NEW.time, INTERVAL 2 MONTH) DO
                    -- 检查 TrainingPlan 表中是否存在该 username 和 next_time 的记录
                    IF EXISTS (SELECT 1 FROM TrainingPlan WHERE username = NEW.username AND time = next_time) THEN
                        -- 如果存在，更新 exercise_duration
                        UPDATE TrainingPlan
                        SET exercise_duration = exercise_duration + course_duration
                        WHERE username = NEW.username AND time = next_time;
                    ELSE
                        -- 如果不存在，插入一条新记录
                        INSERT INTO TrainingPlan (id, username, time, exercise_duration)
                        VALUES (
                            NEW.id,
                            NEW.username,
                            next_time,
                            course_duration
                        );
                    END IF;

                    -- 计算下一个时间点
                    SET next_time = DATE_ADD(next_time, INTERVAL interval_days DAY);
                END WHILE;
            END;
        """)
        # 触发器 3: 当用户取消订阅课程时，课程的人数减少
        cursor.execute("""
            CREATE TRIGGER decrement_course_people
            AFTER DELETE ON CourseRegistration
            FOR EACH ROW
            BEGIN
                UPDATE Course
                SET total_people = total_people - 1
                WHERE course = OLD.course;
            END;
        """)
        cursor.close()
    except Error as e:
        print(f"创建触发器时发生错误: {e}")

def print_tables(connection):
    try:
        cursor = connection.cursor()

        # 打印 Users 表
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        print("Users 表内容:")
        for user in users:
            print(user)

        # 打印 Course 表
        cursor.execute("SELECT * FROM Course")
        courses = cursor.fetchall()
        print("\nCourse 表内容:")
        for course in courses:
            print(course)
         # 查询 ExerciseTime 表
        cursor.execute("SELECT * FROM ExerciseTime")
        exercise_times = cursor.fetchall()

        # 打印表头
        print("ExerciseTime 表内容:")
        print("{:<5} {:<10} {:<20} {:<10}".format("ID", "Username", "Time", "Duration"))

        # 打印每一行数据
        for row in exercise_times:
            id, username, time, exercise_duration = row
            print("{:<5} {:<10} {:<20} {:<10}".format(id, username, str(time), exercise_duration))

        cursor.close()
    except Error as e:
        print(f"打印表内容时发生错误: {e}")
def generate_exercise_time(connection):
    try:
        cursor = connection.cursor()

        # 获取所有用户
        cursor.execute("SELECT id, username FROM Users")
        users = cursor.fetchall()

        # 生成 ExerciseTime 数据
        for user in users:
            user_id, username = user
            # 为每个用户生成 3 条锻炼记录
            for _ in range(3):
                # 随机生成锻炼时间（过去 30 天内）
                exercise_time = datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
                # 随机生成锻炼时长（10 到 120 分钟）
                exercise_duration = random.randint(10, 120)
                # 插入数据
                cursor.execute("""
                    INSERT INTO ExerciseTime (id, username, time, exercise_duration)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, username, exercise_time, exercise_duration))

        # 提交事务
        connection.commit()
        cursor.close()
        print("ExerciseTime 数据生成成功！")
    except Error as e:
        print(f"生成 ExerciseTime 数据时发生错误: {e}")

def simulate_course_registration(connection):
    try:
        cursor = connection.cursor()

        # 获取所有用户
        cursor.execute("SELECT id, username FROM Users")
        users = cursor.fetchall()

        # 获取所有课程
        cursor.execute("SELECT course FROM Course")
        courses = [row[0] for row in cursor.fetchall()]

        # 为每个用户订阅 1 到 2 门课程（跳过 admin 用户）
        for user in users:
            user_id, username = user
            if username == 'admin':
                continue  # 跳过 admin 用户
            print(username)
            # 随机选择 1 到 2 门课程
            selected_courses = random.sample(courses, k=random.randint(1, 2))
            for course in selected_courses:
                # 生成订阅时间（过去 30 天内）
                registration_time = datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
                # 插入数据
                cursor.execute("""
                    INSERT INTO CourseRegistration (id, username, time, course)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, username, registration_time, course))

        # 提交事务
        connection.commit()
        cursor.close()
        print("CourseRegistration 数据模拟成功！")
    except Error as e:
        print(f"模拟 CourseRegistration 数据时发生错误: {e}")

def get_password_by_username(username):
    """
    根据用户名查询密码
    :param connection: 数据库连接对象
    :param username: 要查询的用户名
    :return: 返回密码（如果找到），否则返回 None
    """
    try:
        cursor = connection.cursor()
        # 查询 Users 表中指定用户名的密码
        cursor.execute("SELECT password FROM Users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]  # 返回密码
        else:
            return None  # 用户名不存在
    except Error as e:
        print(f"查询密码时发生错误: {e}")
        return None
def get_training_plan_for_current_month(username):
    """
    查询指定用户本月的训练计划
    :param username: 用户名
    :return: 返回本月的训练计划列表
    """
    try:
        cursor = connection.cursor()
        # 获取当前日期的月份和年份
        current_year = datetime.now().year
        current_month = datetime.now().month

        # 查询 TrainingPlan 表中本月的训练计划
        cursor.execute("""
            SELECT time, course, exercise_duration
            FROM TrainingPlan
            WHERE username = %s AND YEAR(time) = %s AND MONTH(time) = %s
        """, (username, current_year, current_month))

        _, days_in_month = calendar.monthrange(current_year, current_month)

        result = cursor.fetchall()
        result_list = [0] * days_in_month  # 初始化一个长度为 31 的列表，用于存储每天的训练计划
        for row in result:
            time, course, exercise_duration = row
            # print(f"时间: {time}, 课程: {course}, 训练时长: {exercise_duration}分钟")
            result_list[time.day - 1] = exercise_duration  # 将训练时长存储到对应的日期位置
        cursor.close()
        return result_list  # 返回训练计划列表
    except Error as e:
        print(f"查询本月训练计划时发生错误: {e}")
        return []
def get_exercise_records_for_current_month(username):
    """
    查询指定用户本月的锻炼记录
    :param username: 用户名
    :return: 返回本月的锻炼记录列表
    """
    try:
        cursor = connection.cursor()
        # 获取当前日期的月份和年份
        current_year = datetime.now().year
        current_month = datetime.now().month

        # 查询 ExerciseTime 表中本月的锻炼记录
        cursor.execute("""
            SELECT time, exercise_duration
            FROM ExerciseTime
            WHERE username = %s AND YEAR(time) = %s AND MONTH(time) = %s
        """, (username, current_year, current_month))
        _, days_in_month = calendar.monthrange(current_year, current_month)
        result_list = [0] * days_in_month  # 初始化一个长度为 31 的列表，用于存储每天的训练计划

        result = cursor.fetchall()
        for row in result:
            time, exercise_duration = row
            # print(f"时间: {time}, 训练时长: {exercise_duration}分钟")
            result_list[time.day - 1] = exercise_duration  # 将训练时长存储到对应的日期位置
        cursor.close()
        return result_list  # 返回锻炼记录列表
    except Error as e:
        print(f"查询本月锻炼记录时发生错误: {e}")
        return []
def save_today_exercise_time(username, exercise_duration):
    """
    存储用户今天的锻炼时间
    :param username: 用户名
    :param exercise_duration: 本次锻炼时长（分钟）
    """
    try:
        cursor = connection.cursor()
        # 获取今天的日期
        today = datetime.now().date()

        # 检查当天是否已有锻炼记录
        cursor.execute("""
            SELECT id, exercise_duration
            FROM ExerciseTime
            WHERE username = %s AND DATE(time) = %s
        """, (username, today))
        result = cursor.fetchone()

        if result:
            # 如果有记录，更新锻炼时长
            record_id, current_duration = result
            new_duration = current_duration + exercise_duration
            cursor.execute("""
                UPDATE ExerciseTime
                SET exercise_duration = %s
                WHERE id = %s AND username = %s AND DATE(time) = %s
            """, (new_duration, record_id, username, today))
            print(f"更新锻炼记录：用户 {username} 今天的锻炼时长更新为 {new_duration} 分钟")
        else:
            # 如果没有记录，插入新记录
            cursor.execute("""
                INSERT INTO ExerciseTime (id, username, time, exercise_duration)
                VALUES ((SELECT id FROM Users WHERE username = %s), %s, %s, %s)
            """, (username, username, datetime.now(), exercise_duration))
            print(f"新增锻炼记录：用户 {username} 今天的锻炼时长为 {exercise_duration} 分钟")

        # 提交事务
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"存储锻炼时间时发生错误: {e}")

def get_all_courses():
    """
    获取当前所有课程
    :param connection: 数据库连接对象
    :return: 返回所有课程的列表
    """
    try:
        cursor = connection.cursor()
        # 查询 Course 表中的所有课程
        cursor.execute("SELECT course, discription, duration FROM Course")
        courses = cursor.fetchall()
        cursor.close()
        # print("所有课程:")
        out_list = []
        for course in courses:
            out_list.append(course[0])
            # print(course[0])
        return out_list  # 返回课程列表
    except Error as e:
        print(f"获取课程时发生错误: {e}")
        return []

def get_user_registered_courses(username):
    """
    获取指定用户已报名的课程
    :param connection: 数据库连接对象
    :param username: 用户名
    :return: 返回用户已报名课程的列表
    """
    try:
        cursor = connection.cursor()
        # 查询 CourseRegistration 表中指定用户的课程
        cursor.execute("""
            SELECT course, time
            FROM CourseRegistration
            WHERE username = %s
        """, (username,))
        registered_courses = cursor.fetchall()
        out_list = []
        for course in registered_courses:
            out_list.append(course[0])
            # print(course[0])
        cursor.close()
        return out_list  # 返回用户已报名课程列表
    except Error as e:
        print(f"获取用户已报名课程时发生错误: {e}")
        return []
def drop_course(username, course_name):
    """
    删除用户的课程报名记录
    :param username: 用户名
    :param course_name: 课程名称
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM CourseRegistration
            WHERE username = %s AND course = %s
        """, (username, course_name))
        connection.commit()
        cursor.close()
        print(f"用户 {username} 已成功退选课程: {course_name}")
    except Error as e:
        print(f"退选课程时发生错误: {e}")


def register_course(username, course_name):
    """
    添加用户的课程报名记录
    :param username: 用户名
    :param course_name: 课程名称
    """
    try:
        cursor = connection.cursor()
        # 获取当前时间作为报名时间
        registration_time = datetime.now()
        cursor.execute("""
            INSERT INTO CourseRegistration (id, username, time, course)
            VALUES ((SELECT id FROM Users WHERE username = %s), %s, %s, %s)
        """, (username, username, registration_time, course_name))
        connection.commit()
        cursor.close()
        print(f"用户 {username} 已成功报名课程: {course_name}")
    except Error as e:
        print(f"报名课程时发生错误: {e}")
def get_user_current_month_exercise_time(username):
    """
    查询用户当月实际锻炼总时长
    
    Args:
        connection: 数据库连接对象
        username: 用户名
    
    Returns:
        dict: 包含用户名、月份和总锻炼分钟数的字典
    """
    try:
        cursor = connection.cursor()
        
        # 获取当前年月
        cursor.execute("SELECT YEAR(CURRENT_DATE()), MONTH(CURRENT_DATE())")
        current_year, current_month = cursor.fetchone()
        
        # 查询用户当月的锻炼记录
        cursor.execute("""
            SELECT time, exercise_duration 
            FROM ExerciseTime 
            WHERE username = %s 
            AND MONTH(time) = %s 
            AND YEAR(time) = %s
        """, (username, current_month, current_year))
        
        total_duration = 0
        # 使用游标遍历记录并累计总时长
        for exercise_date, duration in cursor:
            total_duration += duration
        
        result = {
            'username': username,
            'month': f"{current_year}-{current_month}",
            'total_exercise_minutes': total_duration
        }
        
        cursor.close()
        return result["total_exercise_minutes"]
    
    except Exception as e:
        print(f"查询用户锻炼时长时发生错误: {e}")
        return None


def get_user_current_month_planned_exercise_time(username):
    """
    查询用户当月规划锻炼总时长
    
    Args:
        connection: 数据库连接对象
        username: 用户名
    
    Returns:
        tuple: (总结信息字典, 详细计划列表)
    """
    try:
        cursor = connection.cursor()
        
        # 获取当前年月
        cursor.execute("SELECT YEAR(CURRENT_DATE()), MONTH(CURRENT_DATE())")
        current_year, current_month = cursor.fetchone()
        
        # 查询用户当月的训练计划
        cursor.execute("""
            SELECT time, course, exercise_duration 
            FROM TrainingPlan 
            WHERE username = %s 
            AND MONTH(time) = %s 
            AND YEAR(time) = %s
            ORDER BY time
        """, (username, current_month, current_year))
        
        total_planned_duration = 0
        plan_details = []
        
        # 使用游标遍历记录，累计总计划时长并收集详细计划
        for plan_date, course, duration in cursor:
            total_planned_duration += duration
            plan_details.append({
                'date': plan_date.strftime('%Y-%m-%d'),
                'course': course,
                'duration': duration
            })
        
        # 汇总信息
        summary = {
            'username': username,
            'month': f"{current_year}-{current_month}",
            'total_planned_minutes': total_planned_duration
        }
        
        cursor.close()
        return summary["total_planned_minutes"]
    
    except Exception as e:
        print(f"查询用户规划锻炼时长时发生错误: {e}")
        return None
def get_course_participants():
    """
    获取每个课程的人数，并整理成字典形式

    Returns:
        dict: 包含课程名称和对应人数的字典
    """
    try:
        cursor = connection.cursor()
        
        # 查询课程名称和总人数
        cursor.execute("""
            SELECT course, total_people
            FROM Course
        """)
        
        # 将结果整理成字典
        course_participants = {}
        for course, total_people in cursor.fetchall():
            course_participants[course] = total_people
        
        cursor.close()
        return course_participants
    
    except Error as e:
        print(f"获取课程人数时发生错误: {e}")
        return {}
def main():
    #connection = connect_to_database()
    if connection:
        # create_tables(connection)
        # create_indexes(connection)
        # create_triggers(connection)
        # generate_exercise_time(connection)
        # print_tables(connection)
        # simulate_course_registration(connection)
        # print(get_training_plan_for_current_month("wangyi"))
        # print(get_exercise_records_for_current_month("wangyi"))
        # save_today_exercise_time("wangyi", 1)
        # print(get_all_courses())
        # print(get_user_registered_courses("wangyi"))
        # print(get_user_current_month_exercise_time("wangyi"))
        # print(get_user_current_month_planned_exercise_time("wangyi"))
        print(get_course_participants())
        connection.commit()
        connection.close()
        print("数据库操作完成")
    pass

if __name__ == "__main__":
    main()