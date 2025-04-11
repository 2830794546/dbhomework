import flask_cors
from flask import Flask, request, jsonify,render_template,redirect, session, url_for
import db 
app = Flask(__name__)

app.secret_key = '7777777777'  # 用于加密 session 数据，请替换为安全的密钥

# @app.before_request
# def is_login():
#     if request.path == 'login':
#         return None
#     if session.get('username'):
#         return None
#     return redirect('/login')
    
@app.route('/')
def index():
    # 检测用户是否已登录
    if 'username' in session:
        username = session['username']  # 从 session 获取当前登录用户的用户名
        list_plan = db.get_training_plan_for_current_month(username)
        list_record = db.get_exercise_records_for_current_month(username)
        total_plan_duration = db.get_user_current_month_planned_exercise_time(username)
        total_actual_duration = db.get_user_current_month_exercise_time(username)
        return render_template('index.html', list_plan=list_plan, list_record=list_record,total_plan_duration=total_plan_duration, total_actual_duration=total_actual_duration,histroy=db.get_user_summary(username))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        true_password = db.get_password_by_username(username)
        print(f"true_password: {true_password}")
        print(f"username: {username}")
        # 简单的登录验证逻辑（替换为实际的数据库验证）
        if password == true_password:  # 示例用户
            session['username'] = username  # 将用户名存储到 session
            if username == 'admin':
                # 如果是管理员，重定向到管理员页面
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            return render_template('login_new.html', error='Invalid credentials')
    return render_template('login_new.html')

@app.route('/logout')
def logout():
    # 清除 session 数据
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/record_exercisetime', methods=['POST'])
def record_exercisetime():
    # 检测用户是否已登录
    if 'username' in session:
        # 获取表单数据
        exercise_time = request.form.get('exercise_record')  # 获取输入框的值
        exercise_time = int(exercise_time)
        if exercise_time:
            db.save_today_exercise_time(session['username'], exercise_time)  # 保存锻炼时间到数据库
            # print(f"收到锻炼记录: {exercise_time} 分钟")
            # 在这里可以将数据保存到数据库或进行其他处理
            # 示例：db.save_exercise_time(session['username'], exercise_time)
        return redirect(url_for('index'))  # 提交后重定向回主页
    else:
        return redirect(url_for('login'))

# @app.route('/')
# def index():
#     list_plan = db.get_training_plan_for_current_month('wangyi')
#     list_record = db.get_exercise_records_for_current_month('wangyi')
#     return render_template('index.html', list_plan=list_plan, list_record=list_record)
    # return render_template('index.html')

@app.route('/cruse')
def cruse():
    # 检测用户是否已登录
    if 'username' in session:
        cruse_all = db.get_all_courses()  # 获取所有课程
        cruse_now = db.get_user_registered_courses(session['username'])  # 获取用户已报名课程

        # 计算未报名课程
        cruse_not_registered = [course for course in cruse_all if course not in cruse_now]
        course_participants = db.get_course_participants()
        return render_template('cruse.html', cruse_now=cruse_now, cruse_not_registered=cruse_not_registered,course_participants=course_participants)
    else:
        return redirect(url_for('login'))

@app.route('/delete_cruse', methods=['POST'])
def delete_cruse():
    # 检测用户是否已登录
    if 'username' in session:
        db.drop_course(session['username'], request.form['course_name'])
        return redirect(url_for('cruse'))  # 重定向到课程页面
    else:
        return redirect(url_for('login'))
    

@app.route('/add_cruse', methods=['POST'])
def add_cruse():
    # 检测用户是否已登录
    if 'username' in session:
        db.register_course(session['username'], request.form['course_name'])
        return redirect(url_for('cruse'))  # 重定向到课程页面
    else:
        return redirect(url_for('login'))
    
@app.route('/admin')
def admin():
    print(db.get_log_records())
    return render_template('admin.html',user = db.get_exercise_time_records(),logs = db.get_log_records())

if __name__ == '__main__':
    app.run(debug=True)