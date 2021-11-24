'''

    使用者藍圖路由

'''

import re
from flask import render_template, request, flash, redirect, url_for
from . import auth

@auth.route('/register', methods = ['GET', 'POST'])
def register():
    ''' 使用者註冊路由 '''

    # TODO 連接資料庫

    username_list = {'a', 'b', 'c'}
    email_list = {'a@gmail.com'}

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if email in email_list:
            flash('Email 已經被使用')
            return render_template('auth/register.html', email = email, username = username)

        if username in username_list:
            flash('使用者名稱已存在')
            return render_template('auth/register.html', email = email)

        if password1 != password2:
            flash('密碼必須相同')
            return render_template('auth/register.html', email = email, username = username)

        flash('註冊成功')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    ''' 使用者登入路由 '''

    email_list = {'a@gmail.com'}
    password_list = {'a'}

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email not in email_list or password not in password_list:
            flash('帳號或密碼錯誤')

            return redirect(url_for('auth.login'))
        
        return redirect(url_for('main.index'))


    return render_template('auth/login.html')