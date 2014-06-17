from __future__ import with_statement

import sys, os
#sys.path
#sys.path.append('/home/rahul/Projects')

import mongogut
import traceback
from flask import (Blueprint, request, url_for, Response, current_app as app, abort, render_template, jsonify)
import flask
import simplejson as json
#from simplejson import JSONDecodeError
from random import choice
from mongogut.utilities import gettype
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.login import current_user

from mongogut import ptassets as itemsandtags

from mongogut.errors import doabort, MongoGutError

#had to move this to global errors.py
# @app.errorhandler(MongoGutError)
# def handle_error(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


from flask import request, session, g, redirect, url_for, \
     abort, render_template, flash, escape, make_response,  Blueprint

import datetime
from werkzeug import Response
from mongoengine import Document
from bson.objectid import ObjectId
BLUEPRINT_MODE=os.environ.get('BLUEPRINT_MODE', True)
BLUEPRINT_MODE=bool(BLUEPRINT_MODE)
#print "BLUEPRINT MODE", BLUEPRINT_MODE

if not BLUEPRINT_MODE:
    adsgut_app=flask.Flask(__name__)
    adsgut=adsgut_app
else:
    adsgut_blueprint = Blueprint('adsgut', __name__,
                                template_folder="templates",
                                static_folder='static',
                                url_prefix='/adsgut',

    )

    adsgut_app=app
    adsgut=adsgut_blueprint
    from adsabs.extensions import mongoengine
    from adsabs.extensions import solr
    #adsgut_app.config['MONGODB_SETTINGS'] = {'DB': 'adsgut'}


##print dir(adsgut), type(adsgut)
#print "HELLO"
#adsgut.config.from_object(__name__)
if not BLUEPRINT_MODE:
    adsgut.config['TESTING'] = True
    adsgut.config['SECRET_KEY'] = 'flask+mongoengine=<3'
    adsgut.debug = True
    adsgut.config['DEBUG_TB_PANELS'] = (
                 'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
                 'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
                 'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
                 'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                 'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
                 'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
                 'flask.ext.mongoengine.panels.MongoDebugPanel'
                 )

    adsgut.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(adsgut)
    adsgut.config['MONGODB_SETTINGS'] = {'DB': 'adsgut'}
    mongoengine = MongoEngine()
    mongoengine.init_app(adsgut_app)

#App should be set up by now. We'll use the mongo-engine flask extension.
#db = MongoEngine()
#db.init_app(adsgut_app)
#

def todfo(ci):
    cijson=ci.to_json()
    cidict=json.loads(cijson)
    return cidict

def todfl(cil):
    cijsonl=[e.to_json() for e in cil]
    cidictl=[json.loads(e) for e in cijsonl]
    return cidictl


class MongoEngineJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Document):
            return obj.to_mongo()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
    """ jsonify with support for MongoDB ObjectId
    """
    return Response(json.dumps(dict(*args, **kwargs), cls=MongoEngineJsonEncoder), mimetype='application/json')
#BUG; these currently dont have doAborts
#do we need a dictpop? CHECK

#FOR GET
def _dictg(k,d, listmode=False):
    val=d.get(k, [None])
    if d.has_key(k):
        d.pop(k)
    if listmode:
        return val
    else:
        return val[0]

#FOR POST
def _dictp(k,d, default=None):
    val=d.get(k, default)
    if d.has_key(k):
        d.pop(k)
    return val

def _userpostget(g, postdict):
    nick=_dictp('useras', postdict)
    if nick:
        useras=g.db._getUserForNick(g.currentuser, nick)
    else:
        useras=g.currentuser
    return useras

def _userget(g, qdict):
    nick=_dictg('useras', qdict)
    userthere=_dictg('userthere', qdict)
    if nick:
        useras=g.db._getUserForNick(g.currentuser, nick)
    else:
        useras=g.currentuser
    if userthere:
        usernick=useras.nick
    else:
        usernick=False
    return useras, usernick

def _sortget(qdict):
    #a serialixed dict of ascending and field
    sortstring=_dictg('sort', qdict)
    if not sortstring:
        return {'field':'posting__whenposted', 'ascending':False}
    sort={}
    sort['field'], sort['ascending'] = sortstring.split(':')
    sort['ascending']=(sort['ascending']=='True')
    return sort

def _sortpostget(qdict):
    #a serialixed dict of ascending and field
    sortstring=_dictp('sort', qdict)
    if not sortstring:
        return {'field':'posting__whenposted', 'ascending':False}
    sort={}
    sort['field'], sort['ascending'] = sortstring.split(':')
    sort['ascending']=(sort['ascending']=='True')
    return sort

#criteria is a multiple ampersand list, with colon separators.
#eg criteria=basic__fqin:eq:something&criteria=
#we create from it a criteria list of dicts
def _criteriaget(qdict):
    #a serialixed dict of arbitrary keys, with mongo style encoding
    #later we will clamp down on it. BUG
    critlist=_dictg('criteria', qdict, True)
    if not critlist[0]:
        return False
    crit=[]
    for ele in critlist:
        cr={}
        cr['field'], cr['op'], cr['value'] = ele.split(':',2)
        crit.append(cr)
    return crit

def _queryget(qdict):
    #a serialixed dict of arbitrary keys, with mongo style encoding
    #later we will clamp down on it. BUG
    querylist=_dictg('query', qdict, True)
    if not querylist[0]:
        return {}
    q={}
    for ele in querylist:
        field, value = ele.split(':',1)
        if not q.has_key(field):
            q[field]=[]
        q[field].append(value)
    return q

def _pagtupleget(qdict):
    #a serialized tuple of offset, pagesize
    pagtuplestring=_dictg('pagtuple', qdict)
    if not pagtuplestring:
        return None
    plist=pagtuplestring.split(':')
    pagtuple=[int(e) if e else -1 for e in pagtuplestring.split(':')]
    return pagtuple

#currently force a new items each time.
def _itemsget(qdict):
    itemlist=_dictg('items', qdict, True)
    #print "itemlist", itemlist
    if not itemlist[0]:
        return []
    #Possible security hole bug
    return itemlist

def _itemspostget(qdict):
    itemlist=_dictp('items', qdict)
    if not itemlist:
        return []
    #Possible security hole bug
    return itemlist

def _bibcodespostget(qdict):
    itemlist=_dictp('bibcode', qdict)
    if not itemlist:
        return []
    #Possible security hole bug
    return itemlist

def _postablesget(qdict):
    plist=_dictp('postables', qdict)
    if not plist:
        return []
    #Possible security hole bug
    return plist

#used in POST, not in GET
def _itemstagsget(qdict):
    itemstagslist=_dictp('itemsandtags', qdict)
    if not itemstagslist:
        return []
    #Possible security hole bug
    return itemstagslist

#used in POST, not in get
def _tagspecsget(qdict):
    tagspecs=_dictp('tagspecs', qdict)
    if not tagspecs:
        return {}
    #Possible security hole bug
    return tagspecs

#x
import uuid
@adsgut.before_request
def before_request():
    #username=session.get('username', None)
    #BUG: currently get first part of email
    try:
        #username=current_user.get_username().split('@')[0]
        #print "getting user info"
        adsid=current_user.get_username()
        cookieid=current_user.get_id()
    except:
        adsid=None
    #print "USER", adsid, current_user.get_id()
    ##print "POSTER", url_for('adsgut.postForm', itemtypens='ads', itemtypename='pub')
    p=itemsandtags.Postdb(mongoengine)
    w=p.whosdb
    g.db=w
    g.dbp=p
    #BUG; this should change towards an anonymous user being sent back
    if not adsid:
        adsid='anonymouse'
        user=g.db._getUserForAdsid(None, adsid)
    else:
        try:
            user=g.db._getUserForCookieid(None, cookieid)
            if user.adsid != adsid:#user changed their email
                #print "email changed"
                user.adsid = adsid
                user.save(safe=True)
            #print "---------->IN HERE", adsid
        except:
            #print "<----------OR HERE", adsid, sys.exc_info()
            adsgutuser=g.db._getUserForNick(None, 'adsgut')
            adsuser=g.db._getUserForNick(adsgutuser, 'ads')
            #we dont have the cookie, but we might have the adsid, because he was invited earlier
            try:#partially in our database
              user=g.db._getUserForAdsid(None, adsid)
              user.cookieid=cookieid
              user.save(safe=True)
            except:#not at all in our database
              #BUG: IF the next two dont happen transactionally we run into issues. Later we make this transactional
              #this removes the possibility of the user adding a custom nick, for now
              #cookieid=current_user.get_id()
              #user=w.addUser(adsgutuser,{'adsid':adsid})
              #Make sure this one is done on invite
              user=g.db.addUser(adsgutuser,{'adsid':adsid, 'cookieid':cookieid})
            #add the user to the flagship ads app, at the very least, to complete user
            #being in our database
            user, adspubapp = g.db.addUserToMembable(adsuser, 'ads/app:publications', user.nick)


    #superuser if no login BUG: use only for testing

    #currently set to sysuser. Atherwise have user login and set.
    #This should set a user into our mongodb table if needed. BUG
    g.currentuser=user


# @adsgut.route('/login', methods=['GET', 'POST'])
# def login():
#     error=None
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         session['logged_in'] = True
#         flash('You were logged in')
#         return redirect(url_for('index'))
#     return render_template('login.html', error=error, useras=g.currentuser)

# @adsgut.route('/logout')
# def logout():
#     # remove the username from the session if it's there
#     session.pop('username', None)
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('index'))


# #x
# @adsgut.route('/')
# def index():
#     return render_template('index.html', useras=g.currentuser)
# #x
# @adsgut.route('/all')
# def all():
#     groups=g.db.allGroups(g.currentuser)
#     apps=g.db.allApps(g.currentuser)
#     libraries=g.db.allLibraries(g.currentuser)
#     users=g.db.allUsers(g.currentuser)
#     return flask.render_template('index.html', groups=groups, apps=apps, users=users, libraries=libraries)

#######################################################################################################################
#######################################################################################################################

#Information about users, groups, and apps
#TODO: should we support a modicum of user information for others
#like group and app owners?
#x
import simplejson as json
@adsgut.route('/user/<nick>')
def userInfo(nick):
    user=g.db.getUserInfo(g.currentuser, nick)
    postablesother, names = user.membableslibrary(pathinclude_p=True)
    #print "PN", postablesother, names
    #crikey stupid hack to have to do this bcoz of jsonify introspecting
    #mongoengine objects only
    jsons = [e.to_json() for e in postablesother]
    ds=[]
    for i, j in enumerate(jsons):
        d = json.loads(j)
        #print "D", d['fqpn']
        if names[d['fqpn']][0][2]==d['fqpn']:#direct membership overrides all else
            d['reason'] = ''
        else:
            reasons=[e[1] for e in names[d['fqpn']]]
            #print "R1", reasons
            elim=[]
            for j,r in enumerate(reasons):
                if r=='group:public' and len(reasons) > 1:
                    elim.append(j)
            for j in elim:
                del reasons[j]
            #print "R2", reasons
            d['reason'] = ",".join(reasons)
        ds.append(d)

    ujson = jsonify(user=user, postablelibs=ds)
    return ujson

from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email

class InviteForm(Form):
    memberable = TextField('username', validators=[DataRequired(), Email()])
    op = HiddenField(default="invite")
    changerw = BooleanField("Can Post?")
    recaptcha = RecaptchaField()

class InviteFormGroup(Form):
    memberable = TextField('username', validators=[DataRequired(), Email()])
    op = HiddenField(default="invite")
    recaptcha = RecaptchaField()

#x
@adsgut.route('/user/<nick>/profile/html')
def userProfileHtml(nick):
    user=g.db.getUserInfo(g.currentuser, nick)
    return render_template('userprofile.html', theuser=user, useras=g.currentuser)

@adsgut.route('/email/<adsid>/profile/html')
def userProfileFromAdsidHtml(adsid):
    user=g.db.getUserInfoFromAdsid(g.currentuser, adsid)
    return render_template('userprofile.html', theuser=user, useras=g.currentuser)

@adsgut.route('/user/<nick>/profilegroups/html')
def userProfileGroupsHtml(nick):
    user=g.db.getUserInfo(g.currentuser, nick)
    return render_template('userprofilegroups.html', theuser=user, useras=g.currentuser)

@adsgut.route('/email/<adsid>/profilegroups/html')
def userProfileGroupsFromAdsidHtml(adsid):
    user=g.db.getUserInfoFromAdsid(g.currentuser, adsid)
    return render_template('userprofilegroups.html', theuser=user, useras=g.currentuser)

#Direct
@adsgut.route('/user/<nick>/postablesuserisin')
def postablesUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    allpostables=g.db.membablesForUser(g.currentuser, useras)
    groups=[e['fqpn'] for e in allpostables if e['ptype']=='group']
    libraries=[e['fqpn'] for e in allpostables if e['ptype']=='library']
    apps=[e['fqpn'] for e in allpostables if e['ptype']=='app']
    groups.remove("adsgut/group:public")
    libraries.remove("adsgut/library:public")
    libraries.remove(useras.nick+"/library:default")
    return jsonify(groups=groups, libraries=libraries, apps=apps)

@adsgut.route('/user/<nick>/postablesusercanwriteto')
def postablesUserCanWriteTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    allpostables=g.db.membablesUserCanWriteTo(g.currentuser, useras)
    #groups=[e['fqpn'] for e in allpostables if e['ptype']=='group']
    libraries=[e['fqpn'] for e in allpostables if e['ptype']=='library']
    #apps=[e['fqpn'] for e in allpostables if e['ptype']=='app']
    #print "GLA", groups, libraries, apps
    #groups.remove("adsgut/group:public")
    libraries.remove("adsgut/library:public")
    libraries.remove(useras.nick+"/library:default")
    return jsonify(groups=[], libraries=libraries, apps=[])

#x
@adsgut.route('/user/<nick>/groupsuserisin')
def groupsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=[e['fqpn'] for e in g.db.membablesForUser(g.currentuser, useras, "group")]
    groups.remove("adsgut/group:public")
    return jsonify(groups=groups)

#x
@adsgut.route('/user/<nick>/groupsuserowns')
def groupsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=[e['fqpn'] for e in g.db.ownerOfMembables(g.currentuser, useras, "group")]
    return jsonify(groups=groups)

#x
@adsgut.route('/user/<nick>/groupsuserisinvitedto')
def groupsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=[e['fqpn'] for e in g.db.membableInvitesForUser(g.currentuser, useras, "group")]
    return jsonify(groups=groups)

#x
@adsgut.route('/user/<nick>/appsuserisin')
def appsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=[e['fqpn'] for e in g.db.membablesForUser(g.currentuser, useras, "app")]
    return jsonify(apps=apps)

#removed apps-user can write to. apps are not modeleld as libraries, but rather as groups.
#we should figure some other way to do this
#x
@adsgut.route('/user/<nick>/appsuserowns')
def appsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=[e['fqpn'] for e in g.db.ownerOfMembables(g.currentuser, useras, "app")]
    return jsonify(apps=apps)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/appsuserisinvitedto')
def appsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=[e['fqpn'] for e in g.db.membableInvitesForUser(g.currentuser, useras, "app")]
    return jsonify(apps=apps)


#does not handle non-direct  inness
@adsgut.route('/user/<nick>/librariesuserisin')
def librariesUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=[e['fqpn'] for e in g.db.membablesUserCanAccess(g.currentuser, useras, "library")]
    return jsonify(libraries=libs)

#BUG: not right
@adsgut.route('/user/<nick>/librariesusercanwriteto')
def librariesUserCanWriteTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=[e['fqpn'] for e in g.db.membablesUserCanWriteTo(g.currentuser, useras, "library")]
    return jsonify(libraries=libs)

#x
@adsgut.route('/user/<nick>/librariesuserowns')
def librariesUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=[e['fqpn'] for e in g.db.ownerOfMembables(g.currentuser, useras, "library")]
    return jsonify(libraries=libs)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/librariesuserisinvitedto')
def librariesUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=[e['fqpn'] for e in g.db.membableInvitesForUser(g.currentuser, useras, "library")]
    return jsonify(libraries=libs)

#BUG currentuser useras here?
@adsgut.route('/user/<nick>/items')
def userItems(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    num, vals=g.dbp.getItemsForQuery(g.currentuser, useras,
       {'group':[useras.nick+"/group:default"]} )
    #userdict={'count':num, 'items':[json.loads(v.to_json()) for v in vals]}
    return jsonify(count=num, items=vals)
#######################################################################################################################
#creating groups and apps
#accepting invites.
#DELETION methods not there BUG

#BUG: check currentuser useras stuff here
#BUG: postable really a tuple. change to reflect that
def createMembable(g, request, ptstr):
    spec={}
    jsonpost=dict(request.json)
    useras=_userpostget(g,jsonpost)
    name=_dictp('name', jsonpost)
    if not name:
        doabort("BAD_REQ", "No Name Specified")
    description=_dictp('description', jsonpost, '')
    spec['creator']=useras.basic.fqin
    spec['name']=name
    spec['description']=description
    postable=g.db.addMembable(g.currentuser, useras, ptstr, spec)
    return postable

@adsgut.route('/group', methods=['POST'])#groupname/description
def createGroup():
    if request.method == 'POST':
        newgroup=createMembable(g, request, "group")
        return jsonify(postable=newgroup)
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/app', methods=['POST'])#name/description
def createApp():
    if request.method == 'POST':
        newapp=createMembable(g, request, "app")
        return jsonify(postable=newapp)
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/library', methods=['POST'])#name/description
def createLibrary():
    if request.method == 'POST':
        newlibrary=createMembable(g, request, "library")
        return jsonify(postable=newlibrary)
    else:
        doabort("BAD_REQ", "GET not supported")

from adsabs.modules.user.user import AdsUser
from adsabs.modules.user.user import send_email_to_user

@adsgut.route('/postable/<po>/<pt>:<pn>/makeinvitations', methods=['POST'])#user/op
def makeInvitations(po, pt, pn):
  fqpn=po+"/"+pt+":"+pn
  if request.method == 'POST':
      if pt=="library":
        form = InviteForm()
      else:
        form = InviteFormGroup()
      if form.validate():
        #specify your own nick for accept or decline
        #print "LALALALALLA", form.memberable.data, form.changerw.data
        # jsonpost=dict(request.form)
        memberable=form.memberable.data
        changerw=False
        if pt=="library":
          changerw=form.changerw.data
        # changerw=_dictp('changerw', jsonpost)
        # if changerw==None:
        #     changerw=False
        if not memberable:
             doabort("BAD_REQ", "No User Specified")
        #print "memberable", memberable, changerw
        potentialuserstring=""
        try:
            user=g.db._getUserForAdsid(g.currentuser, memberable)
        except:
            #print "no such user", memberable
            adsuser = AdsUser.from_email(memberable)
            #print "here", adsuser
            adsgutuser=g.db._getUserForNick(None, 'adsgut')
            adsappuser=g.db._getUserForNick(adsgutuser, 'ads')
            if adsuser==None:#not in giovanni db, just add to ours
              #doabort("BAD_REQ", "No such User")
              #print "q"
              adsgutuser=g.db._getUserForNick(None, 'adsgut')
              #print "q2"
              potentialuser=g.db.addUser(adsgutuser,{'adsid':memberable, 'cookieid':'NOCOOKIEYET-'+str(uuid.uuid4())})
              user=potentialuser
              potentialuserstring="""
              <p>
              The SAO/NASA Astrophysics Data System (ADS) is a Digital Library portal for researchers in Astronomy and
              Physics, operated by the Smithsonian Astrophysical Observatory (SAO) under a NASA grant. The ADS maintains
              three bibliographic databases containing more than 10.8 million records: Astronomy and Astrophysics, Physics,
              and arXiv e-prints. The main body of data in the ADS consists of bibliographic records, which are searchable
              through highly customizable query forms, and full-text scans of much of the astronomical literature which
              can be browsed or searched via our full-text search interface at <a href="http://labs.adsabs.harvard.edu/adsabs/">http://labs.adsabs.harvard.edu/adsabs/</a>."
              </p>
              """
            else:#already in giovanni db, add to ours
              #print "r"
              cookieid = adsuser.get_id()
              adsid = adsuser.get_username()
              user=g.db.addUser(adsgutuser,{'adsid':adsid, 'cookieid':cookieid})
              user, adspubapp = g.db.addUserToMembable(adsappuser, 'ads/app:publications', user.nick)
              potentialuserstring=""
        potentialuserstring2="""
        <p>
        If you already have an account at ADS, you can go to <a href="http://labs.adsabs.harvard.edu/adsabs/user/">http://labs.adsabs.harvard.edu/adsabs/user/</a>, sign in, and click the %s link there to accept.
        </p>
        <p>
        If you do not already have an ADS account, please <a href="http://labs.adsabs.harvard.edu/adsabs/user/signup">Sign up</a>! You will then be able to accept the invite from your account's Groups page.
        </p>
        """
        #ok got user, now invite
        utba, p=g.db.inviteUserToMembable(g.currentuser, g.currentuser, fqpn, user, changerw)
        emailtitle="Invitation to ADS Library %s" % pn
        ptmap={'group':'Group (and associated library)', 'library':"Library"}
        ptmap2={'group':'My Groups', 'library':"Libraries"}
        emailtext="%s has invited you to ADS %s %s." % (g.currentuser.adsid, ptmap[pt], pn)
        emailtext = emailtext+potentialuserstring+potentialuserstring2%ptmap2[pt]
        send_email_to_user(emailtitle, emailtext,[user.adsid])
        passdict={}
        passdict[pt+'owner']=po
        passdict[pt+'name']=pn
        flash("Invite sent", 'success')
        return redirect(url_for("adsgut."+pt+"ProfileHtml", **passdict))
      else:
        junk=1
        #print "ERROES", form.errors
        #print "NOVAL", request.form
      return profileHtmlNotRouted(po, pn, pt, inviteform=form)

@adsgut.route('/postable/<po>/<pt>:<pn>/changes', methods=['POST'])#user/op
def doPostableChanges(po, pt, pn):
    #add permit to match user with groupowner
    fqpn=po+"/"+pt+":"+pn
    if request.method == 'POST':
        #specify your own nick for accept or decline
        #print "LALALALALLA", request.json
        jsonpost=dict(request.json)
        memberable=_dictp('memberable', jsonpost)
        changerw=_dictp('changerw', jsonpost)
        if changerw==None:
            changerw=False
        #for inviting this is nick of user invited.
        #for accepting this is your own nick
        if not memberable:
            doabort("BAD_REQ", "No User Specified")
        op=_dictp('op', jsonpost)
        #print "NICKOP", memberable, op
        if not op:
            doabort("BAD_REQ", "No Op Specified")
        if op=="invite":
            try:
                memberable=g.db._getUserForAdsid(g.currentuser, memberable)
            except:
                adsuser = AdsUser.from_email(memberable)
                if adsuser==None:
                    doabort("BAD_REQ", "No such User")
                cookieid = adsuser.get_id()
                adsid = adsuser.get_username()
                adsgutuser=g.db._getUserForNick(None, 'adsgut')
                adsuser=g.db._getUserForNick(adsgutuser, 'ads')
                memberable=g.db.addUser(adsgutuser,{'adsid':adsid, 'cookieid':cookieid})
                memberable, adspubapp = g.db.addUserToMembable(adsuser, 'ads/app:publications', memberable.nick)

            utba, p=g.db.inviteUserToMembable(g.currentuser, g.currentuser, fqpn, memberable, changerw)
            emailtitle="Invitation to ADS Library %s" % pn
            emailtext="%s has invited you to ADS Library %s. Go to your libraries page to accept." % (g.currentuser.adsid, pn)
            send_email_to_user(emailtitle, emailtext,[memberable.adsid])

            return jsonify({'status':'OK', 'info': {'invited':utba.nick, 'to':fqpn}})
        elif op=='accept':
            memberable=g.db._getUserForAdsid(g.currentuser, memberable)
            me, p=g.db.acceptInviteToMembable(g.currentuser, fqpn, memberable)
            return jsonify({'status':'OK', 'info': {'invited':me.nick, 'to': fqpn, 'accepted':True}})
        elif op=='decline':
            memberable=g.db._getUserForAdsid(g.currentuser, memberable)
            #BUG add something to invitations to mark declines.
            return jsonify({'status': 'OK', 'info': {'invited':memberable, 'to': fqpn, 'accepted':False}})
        elif op=='changeowner':
            #you must be the current owner
            memberable=g.db._getUserForAdsid(g.currentuser, memberable)
            newo, p=g.db.changeOwnershipOfMembable(g.currentuser, g.currentuser, fqpn, memberable)
            return jsonify({'status': 'OK', 'info': {'changedto':memberable, 'for': fqpn}})
        elif op=='togglerw':
            #here memberable could be a user or a group (whose membership to library you are toggling)
            #in either case here we need the fqin
            mtype=gettype(memberable)
            memberable=g.db._getMemberableForFqin(g.currentuser, mtype, memberable)
            mem, p = g.db.toggleRWForMembership(g.currentuser, g.currentuser, fqpn, memberable)
            return jsonify({'status': 'OK', 'info': {'user':memberable, 'for': fqpn}})
        elif op=='description':
            description=_dictp('description', jsonpost,'')
            mem, p = g.db.changeDescriptionOfMembable(g.currentuser, g.currentuser, fqpn, description)
            return jsonify({'status': 'OK', 'info': {'user':memberable, 'for': fqpn}})
        else:
            doabort("BAD_REQ", "No Op Specified")
    else:
        doabort("BAD_REQ", "GET not supported")



#DEPRECATED: REMOVE
@adsgut.route('/group/<groupowner>/group:<groupname>/doinvitation', methods=['POST'])#user/op
def doInviteToGroup(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        #specify your own nick for accept or decline
        jsonpost=dict(request.json)
        nick=_dictp('userthere', jsonpost)
        #for inviting this is nick of user invited.
        #for accepting this is your own nick
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        op=_dictp('op', jsonpost)
        if not op:
            doabort("BAD_REQ", "No Op Specified")
        if op=="invite":
            utba, p=g.db.inviteUserToMembableUsingNick(g.currentuser, fqgn, nick)
            return jsonify({'status':'OK', 'info': {'invited':utba.nick, 'to':fqgn}})
        elif op=='accept':
            me, p=g.db.acceptInviteToMembable(g.currentuser, fqgn, nick)
            return jsonify({'status':'OK', 'info': {'invited':me.nick, 'to': fqgn, 'accepted':True}})
        elif op=='decline':
            #BUG add something to invitations to mark declines.
            return jsonify({'status': 'OK', 'info': {'invited':nick, 'to': fqgn, 'accepted':False}})
        elif op=='decline':
            #BUG add something to invitations to mark declines.
            return jsonify({'status': 'OK', 'info': {'invited':nick, 'to': fqgn, 'accepted':False}})
        else:
            doabort("BAD_REQ", "No Op Specified")
    else:
        doabort("BAD_REQ", "GET not supported")

#BUG: user leakage as we do user info for all users in group. another users groups should not be obtainable
#BUG: should this handle a general memberable? must use a SHOWNFIELDS

#BUG: do we want a useras here? Also BUG:no existing version for tag, or POST to changer generable ownerable info yet
def addMemberToPostable(g, request, fqpn):
    jsonpost=dict(request.json)
    #BUG:need fqun right now. work with nicks later
    #print jsonpost
    fqmn=_dictp('member', jsonpost)
    changerw=_dictp('changerw', jsonpost)
    #print "for fqpmn", fqmn, changerw
    if not changerw:
        changerw=False
    # if not g.currentuser.nick:
    #     doabort("BAD_REQ", "No User Specified")
    user, postable=g.db.addMemberableToMembable(g.currentuser, g.currentuser, fqpn, fqmn, changerw)
    #print "here"
    return user, postable

def getMembersOfMembable(g, request, fqpn):
    useras=g.currentuser
    users=g.db.membersOfMembableFromFqin(g.currentuser,useras,fqpn)
    userdict={'users':users}
    return userdict

def getInvitedsForMembable(g, request, fqpn):
    useras=g.currentuser
    users=g.db.invitedsForMembableFromFqin(g.currentuser,useras,fqpn)
    userdict={'users':users}
    return userdict

@adsgut.route('/group/<groupowner>/group:<groupname>/inviteds')
def groupInviteds(groupowner, groupname):
    fqgn=groupowner+"/group:"+groupname
    userdict=getInvitedsForMembable(g, request, fqgn)
    return jsonify(userdict)

@adsgut.route('/library/<libraryowner>/library:<libraryname>/inviteds')
def libraryInviteds(libraryowner, libraryname):
    fqln=libraryowner+"/library:"+libraryname
    userdict=getInvitedsForMembable(g, request, fqln)
    return jsonify(userdict)

@adsgut.route('/group/<groupowner>/group:<groupname>/members', methods=['GET', 'POST'])#user
def addMembertoGroup_or_groupMembers(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        member, group=addMemberToPostable(g, request, fqgn)
        return jsonify({'status':'OK', 'info': {'member':member.basic.fqin, 'type':'group', 'postable':group.basic.fqin}})
    else:
        userdict=getMembersOfMembable(g, request, fqgn)
        return jsonify(userdict)

@adsgut.route('/app/<appowner>/app:<appname>/members', methods=['GET', 'POST'])#user
def addMemberToApp_or_appMembers(appowner, appname):
    #add permit to match user with groupowner
    fqan=appowner+"/app:"+appname
    if request.method == 'POST':
        member, app=addMemberToPostable(g, request, fqan)
        return jsonify({'status':'OK', 'info': {'member':member.basic.fqin, 'type':'app', 'postable':app.basic.fqin}})
    else:
        userdict=getMembersOfMembable(g, request, fqan)
        return jsonify(userdict)


#deprecare library for postable
@adsgut.route('/library/<libraryowner>/library:<libraryname>/members', methods=['GET', 'POST'])#user
def addMemberToLibrary_or_libraryMembers(libraryowner, libraryname):
    #add permit to match user with groupowner
    fqln=libraryowner+"/library:"+libraryname
    if request.method == 'POST':
        member, library=addMemberToPostable(g, request, fqln)
        return jsonify({'status':'OK', 'info': {'member':member.basic.fqin, 'type':'library', 'postable':library.basic.fqin}})
    else:
        userdict=getMembersOfMembable(g, request, fqln)
        return jsonify(userdict)

@adsgut.route('/postable/<po>/<pt>:<pn>/members', methods=['GET', 'POST'])#user
def addMemberToPostable_or_postableMembers(po, pt, pn):
    fqpn=po+"/"+pt+":"+pn
    if request.method == 'POST':
        #print "rf", request, fqpn
        member, postable=addMemberToPostable(g, request, fqpn)
        dictis = {'status':'OK', 'info': {'member':member.basic.fqin, 'type':pt, 'postable':postable.basic.fqin}}
        #print "DICTIS", dictis
        return jsonify(dictis)
    else:
        userdict=getMembersOfMembable(g, request, fqpn)
        return jsonify(userdict)

@adsgut.route('/memberremove', methods=['POST'])
def memberremove():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        fqpn = _dictp('fqpn', jsonpost)
        useras = _userpostget(g, jsonpost)
        member = _dictp('member', jsonpost)
        if fqpn is None:
            doabort("BAD_REQ", "No postable specified for member removal")
        g.db.removeMemberableFromMembable(g.currentuser, useras, fqpn, member)
        return jsonify({'status':'OK'})

@adsgut.route('/membableremove', methods=['POST'])
def membableremove():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        fqpn = _dictp('fqpn', jsonpost)
        useras = _userpostget(g, jsonpost)
        if fqpn is None:
            doabort("BAD_REQ", "No membable specified for  removal")
        g.db.removeMembable(g.currentuser, useras, fqpn)
        return jsonify({'status':'OK'})

#######################################################################################################################
#######################################################################################################################
def postable(ownernick, name, ptstr):
    fqpn=ownernick+"/"+ptstr+":"+name
    postable, owner, creator=g.db.getMembableInfo(g.currentuser, g.currentuser, fqpn)
    isowner=False
    if g.db.isOwnerOfPostable(g.currentuser, g.currentuser, postable):
        isowner=True
    return postable, isowner, owner.presentable_name(), creator.presentable_name()


#POST/GET in a lightbox?
@adsgut.route('/group/html')
def creategrouphtml():
    pass

#get group info
#x
@adsgut.route('/group/<groupowner>/group:<groupname>')
def groupInfo(groupowner, groupname):
    g, io, on, cn = postable(groupowner, groupname, "group")
    return jsonify(group=g, oname = on, cname = cn)

#x
@adsgut.route('/postable/<groupowner>/group:<groupname>/profile/html')
def groupProfileHtml(groupowner, groupname):
    return profileHtmlNotRouted(groupowner, groupname, "group", inviteform=None)


#POST/GET in a lightbox?
@adsgut.route('/app/html')
def createapphtml():
    pass

#x
@adsgut.route('/app/<appowner>/app:<appname>')
def appInfo(appowner, appname):
    a, io, on, cn = postable(appowner, appname, "app")
    return jsonify(app=a, oname = on, cname = cn)

#x
@adsgut.route('/postable/<appowner>/app:<appname>/profile/html')
def appProfileHtml(appowner, appname):
    return profileHtmlNotRouted(appowner, appname, "app", inviteform=None)


#POST/GET in a lightbox?
@adsgut.route('/library/html')
def createlibraryhtml():
    pass

#get group info
#x
@adsgut.route('/library/<libraryowner>/library:<libraryname>')
def libraryInfo(libraryowner, libraryname):
    l, io, on, cn = postable(libraryowner, libraryname, "library")
    return jsonify(library=l, oname=on, cname=cn)

#x
@adsgut.route('/postable/<libraryowner>/library:<libraryname>/profile/html')
def libraryProfileHtml(libraryowner, libraryname):
    return profileHtmlNotRouted(libraryowner, libraryname, "library", inviteform=None)

def profileHtmlNotRouted(powner, pname, ptype, inviteform=None):
    p, owner, on, cn=postable(powner, pname, ptype)
    if not inviteform:
      if ptype=="library":
        inviteform = InviteForm()
      else:
        inviteform = InviteFormGroup()
    return render_template(ptype+'profile.html', thepostable=p, owner=owner, inviteform=inviteform, useras=g.currentuser, po=powner, pt=ptype, pn=pname)

@adsgut.route('/postable/<nick>/library:default/filter/html')
def udlHtml(nick):
    return postableFilterHtml(nick, "library", "default")

@adsgut.route('/postablefromadsid/<adsid>/library:default/filter/html')
def udlHtmlFromAdsid(adsid):
    user=g.db.getUserInfoFromAdsid(g.currentuser, adsid)
    return postableFilterHtml(user.nick, "library", "default")

@adsgut.route('/postable/adsgut/library:public/filter/html')
def publicHtml():
    return postableFilterHtml("adsgut", "library", "public")

@adsgut.route('/postable/<po>/<pt>:<pn>/filter/html')
def postableFilterHtml(po, pt, pn):
    querystring=request.query_string
    p, owner, on, cn=postable(po, pn, pt)
    pflavor='pos'
    if pn=='public' and po=='adsgut' and pt=='library':
        pflavor='pub'
    if pn=='default' and pt=='library':
        tqtype='stags'
        pflavor='udg'
    else:
        pflavor=p.basic.fqin
        tqtype='tagname'
    tqtype='tagname'
    #BUG using currentuser right now. need to support a notion of useras
    return render_template('postablefilter.html', p=p, po=po, pt=pt, pn=pn, pflavor=pflavor, querystring=querystring, tqtype=tqtype, useras=g.currentuser, owner=owner)


#######################################################################################################################
#######################################################################################################################

def _getContext(q):
    #BUG:user contexts will be hidden. So this will change
    if not q.has_key('cuser'):
        return None
    context={}
    if q['cuser']=="True":
        context['user']=True
    else:
        context['user']=False
    if not q.has_key('ctype'):
        return None
    context['type']=q['ctype']
    if not q.has_key('cvalue'):
        return None
    context['value']=q['cvalue']
    return context



#these might be supersed by tagging based results to populate the left side

#The users simple tags, not singletonmode (ie no notes), not libraries
@adsgut.route('/user/<nick>/tagsuserowns')
def tagsUserOwns(nick):
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    tagtype= _dictg('tagtype', query)
    #will not get notes
    stags=g.dbp.getTagsAsOwnerOnly(g.currentuser, useras, tagtype)
    stagdict={'simpletags':set([e.basic.name for e in stags[1]])}
    return jsonify(stagdict)

#these are the simple tags user owns as well as can write to by dint of giving it to a group.
@adsgut.route('/user/<nick>/tagsusercanwriteto')
def tagsUserCanWriteTo(nick):
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    tagtype= _dictg('tagtype', query)
    fqpn = _dictg('fqpn',query)
    #print "TAGGER", tagtype, fqpn
    #TODO:prevent null fqpn
    stags=g.dbp.getAllTagsForUser(g.currentuser, useras, tagtype, False, fqpn)
    #print "STAGS", stags
    stagdict={'simpletags':set([e.basic.name for e in stags[1]])}
    return jsonify(stagdict)

@adsgut.route('/user/<nick>/tagsasmember')
def tagsUserAsMember(nick):
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    tagtype= _dictg('tagtype', query)
    fqpn = _dictg('fqpn',query)
    #TODO:prevent null fqpn
    stags=g.dbp.getTagsAsMemberOnly(g.currentuser, useras, tagtype, False, fqpn)
    stagdict={'simpletags':set([e.basic.name for e in stags[1]])}
    return jsonify(stagdict)

########################


#################now going to tags and posts#################################

#above 3 stags will be superseded, rolled in
#BUG: no multis are done for now.


#POST posts items into postable, get gets items for postable consistent with user.
#ALL ITEMS in POST MUST BE OF SAME TYPE
@adsgut.route('/postable/<po>/<pt>:<pn>/items', methods=['GET', 'POST'])
def itemsForPostable(po, pt, pn):
    #userthere/[fqins]
    #q={sort?, pagtuple?, criteria?, postable}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        #henceforth this will be names
        items = _itemspostget(jsonpost)
        itemtype=_dictp('itemtype', jsonpost)
        fqpn=po+"/"+pt+":"+pn
        pds=[]
        for name in items:
            #doing this for its idempotency
            itemspec={'name':name, 'itemtype':itemtype}
            i=g.dbp.saveItem(g.currentuser, useras, itemspec)
            i,pd=g.dbp.postItemIntoPostable(g.currentuser, useras, fqpn, i)
            pds.append(pd)
        itempostings={'status':'OK', 'postings':pds, 'postable':fqpn}
        return jsonify(itempostings)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        #BUG find a way of having the usernick in this context be from elsewhere
        #the elsewhere would come from postings and taggings, and confine to this group
        #perhaps all the query funcs would need some re-org
        #print "QQQ",query, request.args
        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        pagtuple = _pagtupleget(query)
        #pagtuple=(2,1)
        criteria= _criteriaget(query)
        postable= po+"/"+pt+":"+pn
        q=_queryget(query)
        #print "Q is", q
        if not q.has_key('postables'):
            q['postables']=[]
        q['postables'].append(postable)
        #print "Q is", q, query, useras, usernick
        #By this time query is popped down
        count, items=g.dbp.getItemsForQuery(g.currentuser, useras,
            q, usernick, criteria, sort, pagtuple)
        return jsonify({'items':items, 'count':count, 'postable':postable})

@adsgut.route('/postable/<po>/<pt>:<pn>/json', methods=['GET'])
def jsonItemsForPostable(po, pt, pn):
    #userthere/[fqins]
    #q={sort?, pagtuple?, criteria?, postable}
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    #BUG find a way of having the usernick in this context be from elsewhere
    #the elsewhere would come from postings and taggings, and confine to this group
    #perhaps all the query funcs would need some re-org
    #print "QQQ",query, request.args
    #need to pop the other things like pagetuples etc. Helper funcs needed
    sort = _sortget(query)
    pagtuple = _pagtupleget(query)
    #pagtuple=(2,1)
    criteria= _criteriaget(query)
    postable= po+"/"+pt+":"+pn
    q=_queryget(query)
    #print "Q is", q
    if not q.has_key('postables'):
        q['postables']=[]
    q['postables'].append(postable)
    #print "Q is", q, query, useras, usernick
    #By this time query is popped down
    count, items=g.dbp.getItemsForQueryWithTags(g.currentuser, useras,
        q, usernick, criteria, sort, pagtuple)
    return jsonify({'items':items, 'count':count, 'postable':postable})

@adsgut.route('/postable/<po>/<pt>:<pn>/csv', methods=['GET'])
def csvItemsForPostable(po, pt, pn):
    #userthere/[fqins]
    #q={sort?, pagtuple?, criteria?, postable}
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    #BUG find a way of having the usernick in this context be from elsewhere
    #the elsewhere would come from postings and taggings, and confine to this group
    #perhaps all the query funcs would need some re-org
    #print "QQQ",query, request.args
    #need to pop the other things like pagetuples etc. Helper funcs needed
    sort = _sortget(query)
    pagtuple = _pagtupleget(query)
    #pagtuple=(2,1)
    criteria= _criteriaget(query)
    postable= po+"/"+pt+":"+pn
    q=_queryget(query)
    #print "Q is", q
    if not q.has_key('postables'):
        q['postables']=[]
    q['postables'].append(postable)
    #print "Q is", q, query, useras, usernick
    #By this time query is popped down
    count, items=g.dbp.getItemsForQueryWithTags(g.currentuser, useras,
        q, usernick, criteria, sort, pagtuple)
    csvstring="#count="+str(count)+",postable="+postable+"\n"
    for i in items:
        s=i['basic']['name']
        for t in i['tags']:
            l=s+","+t
            csvstring=csvstring+l+"\n"
        if len(i['tags'])==0:
            csvstring=csvstring+s+",\n"
    return Response(csvstring, mimetype='text/csv')

@adsgut.route('/library/<libraryowner>/library:<libraryname>/items')
def libraryItems(libraryowner, libraryname):
    return itemsForPostable(libraryowner, "library", libraryname)

@adsgut.route('/app/<appowner>/app:<appname>/items')
def appItems(appowner, appname):
    return itemsForPostable(appowner, "app", appname)

@adsgut.route('/group/<groupowner>/group:<groupname>/items')
def groupItems(groupowner, groupname):
    return itemsForPostable(groupowner, "group", groupname)

#For the RHS, given a set of items. Should this even be exposed as such?
#we need it for post, but goes the GET make any sense?
#CHECK: and is it secure?
#this is post tagging into postable for POST

@adsgut.route('/postable/<po>/<pt>:<pn>/taggings', methods=['GET', 'POST'])
def taggingsForPostable(po, pt, pn):
    #userthere/fqin/fqtn
    #q={sort?, criteria?, postable}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itemsandtags = _itemstagsget(jsonpost)

        fqpn=po+"/"+pt+":"+pn
        tds=[]
        for d in itemsandtags:
            fqin=d['fqin']
            fqtn=d['fgtn']
            td=g.dbp.getTaggingDoc(g.currentuser, useras, fqin, fqtn)
            i,t,td=g.dbp.postTaggingIntoPostable(g.currentuser, useras, fqpn, td)
            tds.append(td)
        itemtaggings={'status':'OK', 'taggings':tds, 'postable':fqpn}
        return jsonify(itemtaggings)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        criteria= _criteriaget(query)
        postable= po+"/"+pt+":"+pn
        q=_queryget(query)
        if not q.has_key('postables'):
            q['postables']=[]
        q['postables'].append(postable)
        #By this time query is popped down
        count, taggings=g.dbp.getTaggingsForQuery(g.currentuser, useras,
            q, usernick, criteria, sort)
        return jsonify({'taggings':taggings, 'count':count, 'postable':postable})

#GET all tags consistent with user for a particular postable and further query
#Why is this useful? And why tags from taggingdocs?
@adsgut.route('/postable/<po>/<pt>:<pn>/tags', methods=['GET'])
def tagsForPostable(po, pt, pn):
    #q={sort?, criteria?, postable}
    query=dict(request.args)
    useras, usernick=_userget(g, query)

    #need to pop the other things like pagetuples etc. Helper funcs needed
    #sort = _sortget(query)
    criteria= _criteriaget(query)
    postable= po+"/"+pt+":"+pn
    q=_queryget(query)
    if not q.has_key('postables'):
        q['postables']=[]
    if pt=='library' and pn=='default':#in saved items get from all postables(libraries) we are in
        # libs=[e['fqpn'] for e in g.db.membablesUserCanWriteTo(g.currentuser, useras, "library")]
        # print "LIBS ARE", libs
        # q['postables']=libs
        q['postables'].append(postable)
    else:
        q['postables'].append(postable)
    #By this time query is popped down
    #count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
    #    q, usernick, criteria)
    count, tags=g.dbp.getTagsForQueryFromPostingDocs(g.currentuser, useras,
        q, usernick, criteria)
    return jsonify({'tags':tags, 'count':count})



@adsgut.route('/itemsremove', methods=['POST'])
def itemsremove():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        fqpn = _dictp('fqpn', jsonpost)
        useras = _userpostget(g, jsonpost)
        items = _itemspostget(jsonpost)
        if fqpn is None:
            doabort("BAD_REQ", "No ipostable specified for item removal")
        for itemfqin in items:
            g.dbp.removeItemFromPostable(g.currentuser, useras, fqpn, itemfqin)
        return jsonify({'status':'OK', 'info':items})

#post saveItems(s), get could get various things such as stags, postings, and taggings
#get could take a bunch of items as arguments, or a query
@adsgut.route('/items', methods=['POST', 'GET'])
def items():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        creator=useras.basic.fqin
        items = _itemspostget(jsonpost)
        itemtype = _dictp('itemtype', jsonpost)
        if not itemtype:
            doabort("BAD_REQ", "No itemtype specified for item")
        for name in items:
            itspec={'creator':creator, 'name':name, 'itemtype':itemtype}
            newitem=g.dbp.saveItem(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':items})
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        pagtuple = _pagtupleget(query)
        criteria= _criteriaget(query)
        #By this time query is popped down
        count, items=g.dbp.getItemsForQuery(g.currentuser, useras,
            query, usernick, criteria, sort, pagtuple)
        return jsonify({'items':items, 'count':count})

#Get tags for a query. We can use post to just create a new tag. [NOT TO DO TAGGING]
#This is as opposed to tagging an item and would be used in biblio apps and such.
#CHECK: currently get coming from taggingdocs. Not sure about this
#BUG: we should make sure it only allows name based tags
#Will let you create multiple tags
#GET again comes from taggingdocs. Why?
@adsgut.route('/tags', methods=['POST', 'GET'])
def tags():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        tagspecs=_tagspecsget(jsonpost)
        newtags=[]
        #SPEC: if u want to create new tags jusr create the dictionary with the key tags.
        for ti in tagspecs['tags']:
            if not ti.has_key('name'):
                doabort('BAD_REQ', "No name specified for tag")
            if not ti.has_key('tagtype'):
                doabort('BAD_REQ', "No tagtypes specified for tag")
            tagspec={}
            tagspec['creator']=useras.basic.fqin
            if ti.has_key('name'):
                tagspec['name'] = ti['name']
            tagspec['tagtype'] = ti['tagtype']
            t=g.dbp.makeTag(g.currentuser, useras, tagspec)
            newtags.append(t)

        #returning the taggings requires a commit at this point
        tags={'status':'OK', 'info':{'item': i.basic.fqin, 'tags':[td for td in newtags]}}
        return jsonify(tags)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        criteria= _criteriaget(query)
        #By this time query is popped down
        count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
            query, usernick, criteria)
        return jsonify({'tags':tags, 'count':count})

#GET tags for an item or POST: tagItem
#Currently GET coming from taggingdocs: BUG: not sure of this

def _setupTagspec(ti, useras):
    #atleast one of name or content must be there (tag or note)
    if not (ti.has_key('name') or ti.has_key('content')):
        doabort('BAD_REQ', "No name or content specified for tag")
    if not ti['tagtype']:
        doabort('BAD_REQ', "No tagtypes specified for tag")
    tagspec={}
    tagspec['creator']=useras.basic.fqin
    if ti.has_key('name'):
        tagspec['name'] = ti['name']
    if ti.has_key('tagmode'):
        tagspec['tagmode'] = ti['tagmode']
    if ti.has_key('content'):
        tagspec['content'] = ti['content']
    tagspec['tagtype'] = ti['tagtype']
    return tagspec

@adsgut.route('/tags/<ns>/<itemname>', methods=['GET', 'POST'])
def tagsForItem(ns, itemname):
    #taginfos=[{tagname/tagtype/description}]
    #q=fieldlist=[('tagname',''), ('tagtype',''), ('context', None), ('fqin', None)]
    ifqin=ns+"/"+itemname
    if request.method == 'POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itemtype=_dictp('itemtype', jsonpost)
        itemspec={'name':itemname, 'itemtype':itemtype}
        fqpn = _dictp('fqpn',jsonpost)
        #KEY:IF i have a item it must exist, so this one is NOT used for items not yet there
        #i=g.dbp._getItem(g.currentuser, ifqin)
        i=g.dbp.saveItem(g.currentuser, useras, itemspec)
        tagspecs=_tagspecsget(jsonpost)
        newtaggings=[]
        if not tagspecs.has_key(itemname):
            doabort('BAD_REQ', "No itemname specified to tag")
        for ti in tagspecs[itemname]:
            tagspec=_setupTagspec(ti, useras)
            #print "TAGSPEC IS", tagspec
            i,t,it,td=g.dbp.tagItem(g.currentuser, useras, i, tagspec)
            newtaggings.append(td)
        #returning the taggings requires a commit at this point
        # taggings={'status':'OK', 'info':{'item': i.basic.fqin, 'tagging':newtaggings}}
        # taggingsdict={}
        # taggingsdict[i.basic.fqin]=(newtaggings.length, newtaggings)
        # return jsonify(taggings=taggingsdict)
        taggingsdict, taggingsthispostable, taggingsdefault= g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras, [ifqin], None, fqpn)
        # taggingsdict={}
        # taggingsdict[ifqin]=(count, taggings)
        #return jsonify({'tags':tags, 'count':count})
        return jsonify(fqpn=fqpn, taggings=taggingsdict, taggingtp=taggingsthispostable, taggingsdefault=taggingsdefault)
    else:
        #print "REQUEST.args", request.args, dict(request.args)
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        fqpn = _dictg('fqpn',query)
        #By this time query is popped down
        #I am not convinced this is how to do this query
        # criteria= _criteriaget(query)
        # criteria.append(['field':'posting__thingtopostfqin', 'op':'eq', 'value':ifqin])
        # count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
        #     query, usernick, criteria, sort)
        #count, tags= g.dbp.getTagsConsistentWithUserAndItems(g.currentuser, useras, [ifqin], sort)
        taggingsdict, taggingsthispostable, taggingsdefault= g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras, [ifqin], sort, fqpn)
        # taggingsdict={}
        # taggingsdict[ifqin]=(count, taggings)
        #return jsonify({'tags':tags, 'count':count})
        return jsonify(fqpn=fqpn, taggings=taggingsdict, taggingtp=taggingsthispostable, taggingsdefault=taggingsdefault)
####These are the fromSpec family of functions for GET

@adsgut.route('/tagsremove/<ns>/<itemname>', methods=['POST'])
def tagsRemoveForItem(ns, itemname):
    #taginfos=[{tagname/tagtype/description}]
    #q=fieldlist=[('tagname',''), ('tagtype',''), ('context', None), ('fqin', None)]
    ifqin=ns+"/"+itemname
    if request.method == 'POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        tagname=_dictp('tagname', jsonpost)
        tagtype=_dictp('tagtype', jsonpost)
        fqpn = _dictp('fqpn',jsonpost)
        #will use useras for the namespace as u should only be removing your own stuff
        fqtn = useras.nick+'/'+tagtype+":"+tagname
        #KEY:IF i have a item it must exist, so this one is NOT used for items not yet there
        #i=g.dbp._getItem(g.currentuser, ifqin)
        #BUGBUGBUG: what about fqpn in here: i only want to untag it in this context
        #print "FQPN is", fqpn
        if fqpn==None:#nuke it
          val=g.dbp.untagItem(g.currentuser, useras, fqtn, ifqin)
        else:#remove tag from postable (should only affect pinpostables)
          val=g.dbp.removeTaggingFromPostable(g.currentuser, useras, fqpn, ifqin, fqtn)
        taggingsdict, taggingsthispostable, taggingsdefault= g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras, [ifqin], None, fqpn)
        # taggingsdict={}
        # taggingsdict[ifqin]=(count, taggings)
        #return jsonify({'tags':tags, 'count':count})
        return jsonify(fqpn=fqpn, taggings=taggingsdict, taggingtp=taggingsthispostable, taggingsdefault=taggingsdefault)


#BUG: havent put in fqpn here yet
#multi item multi tag tagging on POST and get taggings
#TODO: make this consistent with the rest of the stuff returning taggings
@adsgut.route('/items/taggings', methods=['POST', 'GET'])
def itemsTaggings():
    ##name/itemtype/uri/
    #q={useras?, sort?, items}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        items = _itemspostget(jsonpost)
        tagspecs=_tagspecsget(jsonpost)
        itemtype=_dictp('itemtype', jsonpost)
        newtaggings=[]
        for name in items:
            itemspec={'name':name, 'itemtype':itemtype}
            i=g.dbp.saveItem(g.currentuser, useras, itemspec)
            if not tagspecs.has_key(name):
                doabort('BAD_REQ', "No itemname specified to tag")
            for ti in tagspecs[name]:
                tagspec=_setupTagspec(ti, useras)
                i,t,it,td=g.dbp.tagItem(g.currentuser, useras, i, tagspec)
                newtaggings.append(td)
        # itemtaggings={'status':'OK', 'taggings':newtaggings}
        # return jsonify(taggings=newtaggings)
        taggingsdict,_,junk=g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras,
            items, None)
        return jsonify(taggings=taggingsdict)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        #By this time query is popped down
        taggingsdict,_,junk=g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        return jsonify(taggings=taggingsdict)

#multi item multi postable posting on POST and get posts
@adsgut.route('/items/postings', methods=['POST', 'GET'])
def itemsPostings():
    ##name/itemtype/uri/
    #q={useras?, sort?, items}
    if request.method=='POST':
        jsonpost=dict(request.json)
        #print "JSONPOST", request.json
        useras = _userpostget(g, jsonpost)
        items = _itemspostget(jsonpost)
        fqpo = _postablesget(jsonpost)
        itemtype=_dictp('itemtype', jsonpost)
        pds=[]
        for name in items:
            itemspec={'name':name, 'itemtype':itemtype}
            i=g.dbp.saveItem(g.currentuser, useras, itemspec)
            for fqpn in fqpo:
                i,pd=g.dbp.postItemIntoPostable(g.currentuser, useras, fqpn, i)
                pds.append(pd)
        #itempostings={'status':'OK', 'postings':pds}
        # return jsonify(postings=pds)
        postingsdict=g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras,
            items, None)
        return jsonify(postings=postingsdict)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        #print 'QUERY', query
        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        #By this time query is popped down
        postingsdict=g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        return jsonify(postings=postingsdict)

@adsgut.route('/items/taggingsandpostings', methods=['POST', 'GET'])
def itemsTaggingsAndPostings():
    ##name/itemtype/uri/
    #q={useras?, sort?, items}
    if request.method=='POST':
        #"THIS WILL NOT BE TO POST STUFF IN BUT TO GET RESULTS"
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        sort = _sortpostget(jsonpost)
        items = _itemspostget(jsonpost)
        fqpn = _dictp('fqpn',jsonpost)
        #print "ITEMS", items
        #print "FQPN", fqpn
        #print "SORT", sort, "useras", useras
        #By this time query is popped down
        postingsdict=g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras, items, sort)
        taggingsdict, taggingsthispostable, taggingsdefault=g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras, items, sort, fqpn)
        #print "MEEP",taggingsdict, postingsdict
        #print "JEEP",[e.pinpostables for e in taggingsdict['ads/2014MNRAS.437.1698M'][1]]
        #print "MEEP",taggingsthispostable
        return jsonify(fqpn=fqpn, postings=postingsdict, taggings=taggingsdict, taggingtp=taggingsthispostable, taggingsdefault=taggingsdefault)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        ##print 'AAAQUERY', query, request.args
        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        fqpn = _dictg('fqpn',query)
        #By this time query is popped down
        postingsdict=g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        taggingsdict, taggingsthispostable, taggingsdefault=g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort, fqpn)
        #print "MEEP",taggingsthispostable
        return jsonify(fqpn=fqpn, postings=postingsdict, taggings=taggingsdict, taggingtp=taggingsthispostable, taggingsdefault=taggingsdefault)

@adsgut.route('/itemtypes', methods=['POST', 'GET'])
def itemtypes():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = _dictp('name', jsonpost)
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for itemtype")
        itspec['postable'] = _dictp('postable', jsonpost)
        if not itspec['postable']:
            doabort("BAD_REQ", "No postable specified for itemtype")
        newitemtype=g.dbp.addItemType(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newitemtype})
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        criteria= _criteriaget(query)
        isitemtype=True
        count, thetypes=g.dbp.getTypesForQuery(g.currentuser, useras, criteria, usernick, isitemtype)
        return jsonify({'types':thetypes, 'count':count})

#BUG: how to handle bools
@adsgut.route('/tagtypes', methods=['POST', 'GET'])
def tagtypes():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = _dictp('name', jsonpost)
        itspec['tagmode'] = _dictp('tagmode', jsonpost)
        itspec['singletonmode'] = _dictp('singletonmode',jsonpost)
        if not itspec['tagmode']:
            del itspec['tagmode']
        else:
            itspec['tagmode']=bool(itspec['tagmode'])
        if not itspec['singletonmode']:
            del itspec['singletonmode']
        else:
            itspec['singletonmode']=bool(itspec['singletonmode'])
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for itemtype")
        itspec['postable'] = _dictp('postable', jsonpost)
        if not itspec['postable']:
            doabort("BAD_REQ", "No postable specified for itemtype")
        newtagtype=g.dbp.addTagType(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newtagtype})
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        criteria= _criteriaget(query)
        isitemtype=False
        count, thetypes=g.dbp.getTypesForQuery(g.currentuser, useras, criteria, usernick, isitemtype)
        return jsonify({'types':thetypes, 'count':count})

@adsgut.route('/itemsinfo', methods = ['POST', 'GET'])
def itemsinfo():
    if request.method=='POST':
        jsonpost=dict(request.json)
        itemstring=jsonpost.get('items',[''])
        items=itemstring.split(':')
        #print "LLLL", itemstring, items
        theitems=[{'basic':{'name':i.split('/')[-1], 'fqin':i}} for i in items]
    else:
        query=dict(request.args)
        itemstring=query.get('items',[''])[0]
        items=itemstring.split(':')
        theitems=[{'basic':{'name':i.split('/')[-1], 'fqin':i}} for i in items]
    return jsonify({'items': theitems, 'count':len(theitems)})

from config import config

@adsgut.route('/postform/<itemtypens>/<itemtypename>/html', methods=['POST'])
def postForm(itemtypens, itemtypename):
    qstring=""
    #print "NS,NAME", itemtypens, itemtypename
    itemtype=itemtypens+"/"+itemtypename
    if request.method=='POST':
        if itemtype=="ads/pub":
            #print "RVALS", request.values
            current_page=request.referrer
            if request.values.has_key('numRecs'):
                numrecs = request.values.get('numRecs')
            else:
                numrecs = config.SEARCH_DEFAULT_ROWS
            #print "++++++++++++++++++++got bibcodes here", numrecs, config.SEARCH_DEFAULT_ROWS
            if request.values.has_key('bibcode'):
                bibcodes = request.values.getlist('bibcode')
            else:
                try:
                    query_components = json.loads(request.values.get('current_search_parameters'))
                except:
                    #except (TypeError, JSONDecodeError):
                    #@todo: logging of the error
                    return render_template('errors/generic_error.html', error_message='Error. Please try later.')

                #update the query parameters to return only what is necessary
                query_components.update({
                    'facets': [],
                    'fields': ['bibcode'],
                    'highlights': [],
                    'rows': str(numrecs)
                    })

                list_type = request.values.get('list_type')
                if 'sort' not in query_components:
                    from adsabs.core.solr.query_builder import create_sort_param
                    query_components['sort'] = create_sort_param(list_type=list_type)

                req = solr.create_request(**query_components)
                if 'bigquery' in request.values:
                    from adsabs.core.solr import bigquery
                    bigquery.prepare_bigquery_request(req, request.values['bigquery'])
                req = solr.set_defaults(req)
                resp = solr.get_response(req)

                if resp.is_error():
                    return render_template('errors/generic_error.html', error_message='Error while loading bibcodes for posting. Please try later.')

                bibcodes = [x.bibcode for x in resp.get_docset_objects()]
                #print "g2bc here", bibcodes
            items=["ads/"+i for i in bibcodes]
            #print "ITTEMS", items
        elif itemtype=="ads/search":
            itemstring=query.get('items',[''])[0]
    else:
        #print "ITEMTYPE", itemtype
        query=dict(request.args)
        querystring=request.query_string
        itemstring=query.get('items',[''])[0]
        items=itemstring.split(':')
        if query.get('currpage', ''):
            current_page = query.get('currpage')[0]
        else:
            current_page = request.referrer
            if current_page==None:
                current_page=request.url
    theitems=[]
    if itemtype=="ads/pub":
        theitems=[{ 'basic':{'name':i.split('/')[-1],'fqin':i}} for i in items]
    elif itemtype=="ads/search":
        theitems=[{ 'basic':{'name':itemstring,'fqin':'ads/'+itemstring}}]
    #print "THEITEMS", theitems
    #How do we BUG get itemtype. we should redofqin to ads/pub:name as the itemtype
    #always determines the namespace of the item. This would mean name had to be
    #globally unique rather than locally for user usage, unless we have a dual name
    #currently get from url
    singlemode=False
    if len(theitems) ==1:
        singlemode=True
    #this ought to be got from itemtype, currently BUG hack
    nameable=False
    if itemtype=="ads/pub":
        qstring=":".join(items)
    elif itemtype=="ads/search":
        nameable=True
        qstring=itemstring
    if nameable and singlemode:
        nameable=True
    #print "QSTRING", qstring, current_page
    if request.method=="POST":
        return render_template('postform_fancy.html', items=theitems,
            querystring=qstring,
            singlemode=singlemode,
            nameable=nameable,
            itemtype=itemtypename,
            curpage=current_page,
            useras=g.currentuser)
    else:
        return render_template('errors/generic_error.html', error_message='Only POST supported for this for now.')
        #return error instead
        #print "Rendering in postform2"
        return render_template('postform2.html', items=theitems,
            querystring=qstring,
            singlemode=singlemode,
            nameable=nameable,
            itemtype=itemtypename,
            curpage=current_page,
            useras=g.currentuser)


#making the import:

#ADS_CLASSIC_LIBRARIES_URL = config.ADS_CLASSIC_LIBRARIES_URL
ADS_CLASSIC_LIBRARIES_URL = "http://adsabs.harvard.edu/cgi-bin/maint/export_privlib"
import requests

def perform_classic_library_query(parameters, headers, service_url):
    """
    function that performs a get request and returns a json object
    """
    #Perform the request
    r = requests.get(service_url, params=parameters, headers=headers)
    #Check for problems
    try:
        r.raise_for_status()
    except Exception, e:
        exc_info = sys.exc_info()
        app.logger.error("Author http request error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))

    try:
        user_json = r.json()
    except Exception, e:
        exc_info = sys.exc_info()
        app.logger.error("Author JSON decode error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
        r = None
        user_json = {}
    return user_json

#This should probably be done in flask.ext.solrquery but its easier to do it simpler
def perform_solr_bigquery(bibcodes):
    """
    function that performs a POST request and returns a json object
    """
    headers = {'Content-Type': 'big-query/csv'}
    url=config.SOLRQUERY_URL
    qdict = {
        'q':'text:*:*',
        'fq':'{!bitset compression=none}',
        'wt':'json',
        'fl':'bibcode,title,pubdate,author'
    }
    #Perform the request
    qdict['rows']=len(bibcodes)
    rstr = "bibcode\n"+"\n".join(bibcodes)
    #print "RSTR", rstr
    r = requests.post(url, params=qdict, data=rstr, headers=headers)
    #Check for problems
    #print '||||||||||||||||||||||||||||||||||||||||||||||||||||'
    try:
        r.raise_for_status()
    except Exception, e:
        #print "1"
        exc_info = sys.exc_info()
        app.logger.error("Author http request error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))

    try:
        d = r.json()
        #print "2"
    except Exception, e:
        #print "3"
        exc_info = sys.exc_info()
        app.logger.error("Author JSON decode error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
        r = None
        d = {}
    #print "D is", d
    return d

@adsgut.route('/classic/<cookieid>/libraries', methods=['GET'])
def get_classic_libraries(cookieid, password=None):
    #headers BUG add http auth headers here, user ads, password?
    #should also check that we have appropriate cookie somehow?
    headers = {'User-Agent':'ADS Script Request Agent'}
    parameters = {'cookie':cookieid}
    libjson=perform_classic_library_query(parameters, headers, ADS_CLASSIC_LIBRARIES_URL)
    useras=g.db._getUserForCookieid(g.currentuser, cookieid)
    useras.classicimported=True
    useras.save()
    ret=g.dbp.populateLibraries(g.currentuser, useras, libjson)
    if ret:
        return redirect(url_for('adsgut.userProfileHtml', nick=useras.nick))
    else:
        return redirect('/')

@adsgut.route('/bigquery/bibcodes', methods=['POST'])
def get_bigquery_solr():
    if request.method=='POST':
        ##print request.json
        jsonpost=dict(request.json)
        #henceforth this will be names
        bibcodes = _bibcodespostget(jsonpost)
        #print "bcodes", bibcodes
        d=perform_solr_bigquery(bibcodes)
        return jsonify(d)

if __name__ == "__main__":
    adsgut.run(host="0.0.0.0", port=4000)
