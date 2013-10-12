#coding=utf-8
####################################################################################################
# imports
####################################################################################################
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, json, jsonify, make_response
from sqlalchemy import func, or_, and_
from app import app, db, cache
from datetime import datetime
from models import Website, Technology

####################################################################################################
# Functions
####################################################################################################
def get_top_technology(category, order = 'DESC', limit = 5):
    """获取最高使用率的不同种类的技术类型"""
    result = cache.get('top_' + category + '_item_' + order)
    if result is None:

        rs = db.session.execute('select technology.title, count(website.id) from website \
                                left join website_tech on website_tech.website_id = website.id \
                                left join technology on technology.id = website_tech.tech_id \
                                and technology.title in (\
                                    select distinct technology.title from technology \
                                    where technology.category = \'' + category + '\' \
                                    and technology.title != \'Unknown\') \
                                group by technology.title \
                                order by count(website.id) ' + order + ' limit 1,' + str(limit))

        # 添加网站总数
        result = []
        for i in rs:
            if i[0] and i[0] != 'Unknown':
                result.append({
                           'title' : i[0],
                           'total' : i[1]
                           })
        cache.set('top_' + category + '_item_' + order, result, timeout=app.config['SQL_CACHE_TIMEOUT'])
    return result

def filter_website(websites = []):
    """根据设置的规则去过滤所有传入列表websites"""
    json_file = open('./config/filter_website_rules.json', 'r')
    filter_website_rules = json.load(json_file)

    import re
    for r in filter_website_rules:
        (k, v) = r.items()[0]
        websites = [ w for w in websites if not re.search(v, getattr(w, k)) ]

    return websites

####################################################################################################
# Views
####################################################################################################
@app.route('/website/upload', methods = ['POST'])
def website_upload():
    postJson = json.loads(request.data)
    app.logger.debug(postJson)
    if not postJson.has_key('hostname'):
        return jsonify(status = 'missing hostname')

    technologies = []
    for t in postJson['technologies']:
        if not t.has_key('title'):
            return jsonify(status = 'missing technology title')
        if not t.has_key('category'):
            return jsonify(status = 'missing technology category')
        if not t.has_key('url'):
            t['url'] = None
        if not t.has_key('detail'):
            t['detail'] = None

        # 完全一致的技术
        tmpTech = Technology.query.filter_by(title = t['title']).filter_by(category = t['category']).filter_by(detail = t['detail']).first()
        if tmpTech is None:
            tmpTech = Technology(category = t['category'], title = t['title'], detail = t['detail'], url = t['url'])
            db.session.add(tmpTech)

        technologies.append(tmpTech)

    upload = Website.query.filter_by(hostname = postJson['hostname'], port = postJson['port']).first()
    if not upload:
        upload = Website(hostname = postJson['hostname'], port = postJson['port'], title = postJson['title'], ipaddress = postJson['ipaddress'], geo = postJson['geo'], technologies = technologies)
    else:
        upload.last_time    = datetime.now()
        upload.title        = postJson['title']
        upload.technologies = technologies
        upload.ipaddress    = postJson['ipaddress']
        upload.geo          = postJson['geo']
        upload.frequency    = upload.frequency + 1

    db.session.add(upload)
    db.session.commit()

    return jsonify(status = 'ok')


@app.route('/')
@app.route('/index')
def index():
    top_webservers      = get_top_technology('webserver')
    top_webapps         = get_top_technology('web_apps')
    top_oses            = get_top_technology('os')
    top_webtechnologies = get_top_technology('technology')
    return render_template('index.html', 
                            webservers      = top_webservers,
                            webapps         = top_webapps,
                            webtechnologies = top_webtechnologies,
                            oses            = top_oses)

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/tech/<title>')
@app.route('/tech/<title>/<int:page>')
@app.route('/tech/<title>/<int:page>/<int:pagesize>')
def show_tech(title, page = 1, pagesize = app.config['PAGE_SIZE']):
    websites = Website.query\
                .filter(Website.technologies.any(Technology.title == title))\
                .order_by(Website.frequency.desc())\
                .paginate(page, pagesize, True)

    websites.items = filter_website(websites.items)

    return render_template('technology.html', title = title, websites = websites)

@app.route('/json/tech/<title>')
@app.route('/json/tech/<title>/<int:page>')
@app.route('/json/tech/<title>/<int:page>/<int:pagesize>')
def show_tech_json(title, page = 1, pagesize = app.config['PAGE_SIZE']):
    result = cache.get('tech_' + title + '_website_' + str(page) + '_' + str(pagesize))

    if not result:
        websites = Website.query\
                    .filter(Website.technologies.any(Technology.title == title))\
                    .order_by(Website.frequency.desc())\
                    .paginate(page, pagesize, True)

        websites.items = filter_website(websites.items)
        result = []

        for i in websites.items:
            techs = []
            for t in i.technologies:
                if t.title != 'Unknown':
                    techs.append({
                            'title': t.title,
                            'detail' : t.detail
                        })
            result.append({
                            'hostname' : i.hostname,
                            'port'     : i.port,
                            'technologies' : techs
                          })

        cache.set('tech_' + title + '_website_' + str(page) + '_' + str(pagesize), result, timeout=app.config['SQL_CACHE_TIMEOUT'])

    return jsonify(status = 'ok', page = page, pagesize = pagesize, websites = result)

@app.route('/tech/category/<category>')
@app.route('/tech/category/<category>/<int:page>')
@app.route('/tech/category/<category>/<int:page>/<int:pagesize>')
def show_tech_category(category, page = 1, pagesize = app.config['PAGE_SIZE']):
    techs = Technology.query\
    .filter(Technology.category == category)\
    .filter(Technology.title != 'Unknown')\
    .paginate(page, pagesize, True)
    return render_template('tech_category.html', title = category, techs = techs)

@app.route('/search', methods = ['GET', 'POST'])
@app.route('/search/<search_type>', methods = ['GET', 'POST'])
def search(search_type = 'website'):
    page = int(request.args.get('page', 1))
    if request.args.get('word', None):
        search_word = request.args.get('word', None)
    elif request.form.has_key('word'):
        search_word = request.form['word']
    else:
        return render_template('index.html')

    search_words = search_word.strip().split()
    site = None
    tmp_words = []
    #检查site:语法
    for w in search_words:
        if w[:5].lower() == 'site:':
            if w[5] == '\'' or w[5] == '"':
                site = w[5:-1]
            else:
                site = w[5:]
            
            if site[0] == '*':
                site = site[1:]
        else:
            tmp_words.append(w)

    if len(tmp_words) == 0: #只有特殊语法的查询
        #暂时只有site:语法的处理。
        real_search_word = site
        search_type = 'website'
    elif site:
        real_search_word = ' '.join(tmp_words)
        search_type = 'technology'
    else:
        real_search_word = ' '.join(tmp_words)

    if search_type == 'website':
        result = Website.query.filter(Website.hostname.like('%' + real_search_word + ''))\
                 .order_by(Website.frequency.desc())\
                 .paginate(page, app.config['PAGE_SIZE'], True)

        result.items = filter_website(result.items)
        return render_template('search_website.html', search_word = search_word, websites = result)
    elif search_type == 'technology':
        if site is not None:
            result = Website.query.filter(
                        and_(
                            Website.hostname.like('%.' + site),
                            or_(
                                Website.technologies.any(Technology.title.like('%' + real_search_word + '%')),
                                Website.technologies.any(Technology.detail.like('%' + real_search_word + '%'))
                                )
                            )
                     ).paginate(page, app.config['PAGE_SIZE'], True)
            result.items = filter_website(result.items)
            return render_template('search_technology_in_website.html', search_word = search_word, websites = result)
        else:
            result = Technology.query.filter(or_(Technology.title.like('%' + search_word + '%'),\
                     Technology.detail.like('%' + search_word + '%')))\
                     .paginate(page, app.config['PAGE_SIZE'], True)
            return render_template('search_technology.html', search_word = search_word, techs = result)
    else:
        return render_template('index.html')


@app.route('/rule/submit', methods = ['GET', 'POST'])
def submit_rule():
    if request.method == 'GET':
        # 展现提交页面
        return render_template('submit_rule.html')
    else:
        # 提交的数据
        from models import Rule
        # 一些检查
        try:
            if request.form['category'].lower() not in ['webserver', 'technology', 'front_library', 'os', 'webapp']:
                raise Exception('Category is wrong.')
            elif request.form['category'] in ['webserver', 'technology', 'os']:
                if request.form['title'].strip() == '' \
                or request.form['match'].strip() == '' \
                or request.form['regex'].strip() == '':
                    raise Exception('Params are wrong.')
            elif request.form['category'] in ['front_library', 'webapp']:
                if request.form['title'].strip() == '' \
                or request.form['matchType'].strip() == '' \
                or request.form['nodeName'].strip() == '' \
                or request.form['regex'].strip() == '':
                    raise Exception('Params are wrong.')
        except:
            return redirect(url_for('submit_rule'))

####################################################################################################
# Statics
####################################################################################################
@app.route('/robots.txt')
def robots():
    rep = make_response(open('templates/robots.txt', 'r').read())
    rep.headers['Content-type'] = 'text/plain'
    return rep