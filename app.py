from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_mongoengine import MongoEngine
import os, base64, hashlib, re

application = Flask(__name__, static_url_path='', static_folder='public/static', template_folder='public/templates')
application.config["MONGODB_SETTINGS"] = {'DB': "links"}
application.config["PROTECTION"] = "terramag"
application.secret_key = "c8276c054c39335b287012d43a2f252c"

db = MongoEngine(application)

from models import *

@application.route("/")
def home(errors = None):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        links = Link.objects()
        return render_template('dashboard.html',links=links, error=errors)
        
@application.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == application.config["PROTECTION"]:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()
    
@application.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
    
@application.route("/saveurl", methods=['POST'])
def saveurl():
    if request.form['url']:
        if not is_valid_url(request.form['url']):
            return home(errors="Link is not valid")
            
        if not request.form['slug']:
            num = Link.objects().first()
            if num:
                ws = str(num._id + 1).encode('ascii')
                ns = base64.b64encode(ws).decode('utf-8').rstrip('=')
            else:
                ws = str(1).encode('ascii')
                ns = base64.b64encode(ws).decode('utf-8').rstrip('=')
        else:
            ns = request.form['slug']
            
        slugs = Link.objects(slug=ns)
        
        if not slugs:
            slug = Link(
                slug=str(ns),
                url=request.form['url'],
                _id=Link.objects.count() + 1
            )
            slug.save()
            return home()
        else:
            return home(errors="Slug is already in use")
    else:
        return home(errors="URL is not prvided")
        
@application.route('/delete')
def delete():
    slug = request.args.get('slug')
    if slug:
        Link.objects(slug=slug).delete()
    return home()
    
@application.route('/<slug>', strict_slashes=False)
def link(slug):
    obj = Link.objects(slug=slug).first()
    if obj:
        return redirect(obj.url, code=302)
    else:
        abort(404)
        
def is_valid_url(url):
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)
    
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num, alphabet=BASE62):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def decode(string, alphabet=BASE62):
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num
    
if __name__ == "__main__":
    application.run(host='0.0.0.0')