root = exports ? this
$=jQuery
#console.log "In Funcs"
{renderable, ul, li, dl, dt, dd, raw, br, strong} = teacup
w = widgets
prefix = GlobalVariables.ADS_PREFIX+"/adsgut"

monthNamesShort =
  '00': ""
  '01':  "Jan"
  '02':  "Feb"
  '03':  "Mar"
  '04':  "Apr"
  '05':  "May"
  '06':  "Jun"
  '07':  "Jul"
  '08':  "Aug"
  '09':  "Sep"
  '10':  "Oct"
  '11':  "Nov"
  '12':  "Dec"

# {% for auth in doc.author %}
#   {% if loop.index0 < 4 %}{{ auth }}{% endif %}{% if loop.index0 < 3 %};{% endif %}
# {% endfor %}
# {% if loop.length > 4 %}
#   <em>and {{ loop.length - 4 }} coauthors</em>
# {% endif %}

short_authors = (authors) ->
  if authors.length <= 4
    return authors[0..3].join('; ')
  else
    n=authors.length - 4
    return authors[0..3].join('; ')+" <em>and #{n} coauthors</em>"


parse_fqin = (fqin) ->
    vals=fqin.split(':')
    return vals[-1+vals.length]

format_item = ($sel, iteminfo) ->
  #console.log '{',iteminfo,'}'
  [year, month, leave] = if iteminfo.pubdate then iteminfo.pubdate.split('-') else [undefined, undefined, undefined]
  if month is undefined
    pubdate = year ? "unknown"
  else
    pubdate = monthNamesShort[month]+" "+year ? "unknown"

  $sel.append("<span class='pubdate pull-right'><em>published in #{pubdate}</em></span><br/>")
  title = iteminfo.title ? "No title found"
  $sel.append("<span class='title'><strong>#{title}</strong></span><br/>")
  author = iteminfo.author ? ['No authors found']
  $sel.append("<span class='author'>#{short_authors(author)}</span>")

format_tags = (tagtype, $sel, tags, tagqkey)->
  $sel.empty()
  typestring = tagtype.split(':')[1]
  htmlstring="<li class=\"nav-header\">Filter by: #{typestring}</li>"
  for [k,v] in tags
    if tagqkey is 'stags'
      t=v[0]
    else if tagqkey is 'tagname'
      t=k
    else
      t = "CRAP"
    nonqloc=document.location.href.split('?')[0]
    if tagqkey is 'tagname'
      url=nonqloc+"?query=tagtype:#{tagtype}&query=#{tagqkey}:#{t}"
      urla=document.location+"&query=tagtype:#{tagtype}&query=#{tagqkey}:#{t}"
      if nonqloc is document.location.href
        urla=document.location+"?query=tagtype:#{tagtype}&query=#{tagqkey}:#{t}"
    else
      url=nonqloc+"?query=#{tagqkey}:#{t}"
      urla=document.location+"&query=#{tagqkey}:#{t}"
      if nonqloc is document.location.href
        urla=document.location+"?query=#{tagqkey}:#{t}"

    htmlstring = htmlstring+"<li><span><a href=\"#{url}\">#{k}</a>&nbsp;<a href=\"#{urla}\">(+)</a></span></li>"
    ##{v.join(',')}
  $sel.html(htmlstring)

time_format = (timestring) ->
    [d, t] = timestring.split('.')[0].split('T')
    d = d.split('-')[1..2].join('/')
    t = t.split(':')[0..1].join(':')
    return d+" "+t

email_split = (e) ->
  [name, host] = e.split('@')
  hfp = host.split('.')[0]
  return name+'@'+hfp

this_postable = (pval, pview) ->
  #console.log "--", pview, pval
  if pview != 'udg' and pview != 'none'
    if pval==true
      pble = "<i class='icon-comment'></i>&nbsp;&nbsp;"
    else
      pble = ''
  else
    pble = ''
    return pble

format_row = (noteid, notetext, notemode, notetime, user, currentuser, truthiness, pview) ->
  tf = time_format(notetime)
  uf = if user==currentuser then 'me' else email_split(user)
  lock  =  "<i class='icon-lock'></i>&nbsp;&nbsp;"
  nmf = if notemode is '1' then lock else ''
  nt = this_postable(truthiness, pview)
  #console.log "noteid is", noteid, pview, notemode
  outstr = "<tr><td style='white-space: nowrap;'>#{tf}</td><td style='text-align: right;'>#{uf}&nbsp;&nbsp;</td><td>#{nmf}#{nt}</td><td class='notetext'>#{notetext}</td>"
  if uf=='me'
    if pview != 'udg' and notemode =='1'
        outstr = outstr + "<td></td></tr>"
    else
        outstr = outstr + '<td><btn style="cursor:pointer;" class="removenote" id="'+noteid+'"><i class="icon-remove-circle"></i></btn></td></tr>'
  else
    outstr = outstr + "<td></td></tr>"
  return outstr

format_notes_for_item = (fqin, notes, currentuser, pview) ->
  #console.log "current user is", currentuser, notes
  start = '<table class="table-condensed table-striped">'
  end = "</table>"
  lock  =  "<i class='icon-lock'></i>&nbsp;&nbsp;"

  #t3list=("<span>#{t[2]}:  #{t[0]}</span><br/>" for t in notes[fqin])
  #t3list=("<tr><td style='white-space: nowrap;'>#{time_format(t[1])}</td><td style='text-align: right;'>#{if t[2]==currentuser then 'me' else email_split(t[2])}&nbsp;&nbsp;</td><td>#{if t[3] is '1' then lock else ''}#{this_postable(t[4], pview)}#{t[0]}</td></tr>" for t in notes[fqin])
  #t3list=("<tr><td style='white-space: nowrap;'>#{time_format(t[1])}</td><td style='text-align: right;'>#{if t[2]==currentuser then 'me' else email_split(t[2])}&nbsp;&nbsp;</td><td>#{if t[3] is '1' then lock else ''}#{t[0]}</td></tr>" for t in notes[fqin])
  t3list = ( format_row(t[5], t[0], t[3], t[1], t[2], currentuser, t[6], pview) for t in notes[fqin])
  if t3list.length >0
    return start+t3list.join("")+end
  else
    return start+end

# format_tags_for_item = (fqin, stags, nick) ->
#   t2list=("<a href=\"#{prefix}/postable/#{nick}/group:default/filter/html?query=tagname:#{t[0]}&query=tagtype:#{t[1]}\">#{t[0]}</a>" for t in stags[fqin])
#   if t2list.length >0
#     return "<span><i class='icon-tags'></i> "+t2list.join(", ")+"</span><br/>"
#   else
#     return ""

format_tags_for_item = (pview, fqin, stags, memberable, tagajax=true) ->
  #console.log(pview, ">>>",memberable.adsid, stags[fqin])
  pviewbool = (pview == 'none')
  t2list=({url:"#{prefix}/postable/#{memberable.nick}/library:default/filter/html?query=tagname:#{t[0]}&query=tagtype:#{t[1]}", text:"#{t[0]}", id:"#{t[0]}", by: if tagajax then (memberable.adsid==t[2]) else false} for t in stags[fqin])
  #console.log("T@LIST", t2list)
  if t2list.length >0
    return t2list
  else
    return []

parse_fortype = (fqin) ->
    vals = fqin.split(':')
    vals2 = vals[-2+vals.length].split('/')
    return vals2[-1+vals2.length]

# format_postings_for_item = (fqin, postings, nick) ->
#   publ= "adsgut/group:public"
#   priv= "#{nick}/group:default"
#   p2list=("<a href=\"#{prefix}/postable/#{p}/filter/html\">#{parse_fqin(p)}</a>" for p in postings[fqin] when p isnt publ and p isnt priv and parse_fortype(p) isnt "app")
#   if p2list.length >0
#     return "<span><i class='icon-book'></i> "+p2list.join(", ")+"</span><br/>"
#   else
#     return ""

format_postings_for_item = (fqin, postings, nick) ->
  postingslist = _.uniq(postings[fqin])
  publ= "adsgut/library:public"
  priv= "#{nick}/library:default"
  p2list=("<a href=\"#{prefix}/postable/#{p}/filter/html\">#{parse_fqin(p)}</a>" for p in postingslist when p isnt publ and p isnt priv and parse_fortype(p) isnt "app")
  if p2list.length >0
    return p2list
  else
    return []

# format_stuff = (fqin, nick, stags, postings, notes) ->
#   htmlstring= ""
#   htmlstring= htmlstring+format_tags_for_item(fqin, stags, nick)
#   htmlstring= htmlstring+format_postings_for_item(fqin, postings, nick)
#   htmlstring= htmlstring+format_notes_for_item(fqin, notes, nick)
#   return htmlstring

# format_items = ($sel, nick, items, count, stags, notes, postings, formatter, asform=false) ->
#   #console.log "HTML", $sel.html()
#   adslocation = GlobalVariables.ADS_ABSTRACT_BASE_URL;
#   htmlstring = ""
#   #console.log items.length, "ITTABITTA", (i.basic.fqin for i in items), "}}"
#   for i in items
#     fqin=i.basic.fqin
#     ##console.log "whatsup", fqin, items.length, $sel, htmlstring
#     url=adslocation + "#{i.basic.name}"
#     htmlstring = htmlstring + "<#{formatter}><a href=\"#{url}\">#{i.basic.name}</a><br/>"
#     htmlstring=htmlstring+format_tags_for_item(fqin, stags, nick)
#     htmlstring=htmlstring+format_postings_for_item(fqin, postings, nick)
#     htmlstring=htmlstring+format_notes_for_item(fqin, notes, nick)
#     htmlstring=htmlstring+"</#{formatter}>"
#     if asform
#       htmlstring=htmlstring+w.postalnote_form("make note")
#   $sel.append(htmlstring)
#   $('#breadcrumb').append("#{count} items")

get_tags = (tags, tqtype) ->
  #console.log "TAGS", tags
  tdict={}
  if tqtype is 'stags'
    return ([t[3], [t[0]]] for t in tags)
  for t in tags
    [fqtn, user, type, name]=t
    if tdict[name] is undefined
      tdict[name]=[]
    tdict[name].push(fqtn)
  if tqtype is 'tagname'
    return ([k,v] for own k,v of tdict)
  return []

get_taggings = (data) ->
  stags={}
  notes={}
  #console.log "DATA[", data.fqpn,"]", data
  for own k,v of data.taggings
    tp = data.taggingtp[k]
    td = data.taggingsdefault[k]
    tg = v[1]
    #console.log "TGTP", tp.length, td.length
    tp2 = (e[0] or e[1] for e in _.zip(tp,td))
    combi = _.zip(tg, tp2, tp)
    #console.log "1>>>", k,tg
    if v[0] > 0
      if data.fqpn is null or data.fqpn is undefined
        #console.log "here"
        stags[k]=([e[0].posting.tagname, e[0].posting.posttype, e[0].posting.postedby] for e in combi when e[0].posting.posttype is "ads/tagtype:tag")
        notes[k]=([e[0].posting.tagdescription, e[0].posting.whenposted, e[0].posting.postedby, e[0].posting.tagmode, e[1], e[0].posting.tagname, e[2]] for e in combi when e[0].posting.posttype is "ads/tagtype:note")
      else
        #console.log "there"
        stags[k]=([e[0].posting.tagname, e[0].posting.posttype, e[0].posting.postedby] for e in combi when e[0].posting.posttype is "ads/tagtype:tag" and e[2] is true)
        notes[k]=([e[0].posting.tagdescription, e[0].posting.whenposted, e[0].posting.postedby, e[0].posting.tagmode, e[1], e[0].posting.tagname, e[2]] for e in combi when e[0].posting.posttype is "ads/tagtype:note"  and (e[2] is true or e[0].posting.tagmode is '1'))
    else
      stags[k]=[]
      notes[k]=[]
    #console.log "HHHHH", k, notes[k]
  #console.log "HH", stags, data.taggings
  return [stags, notes]

get_groups = (nick, cback) ->
  $.get "#{prefix}/user/#{nick}/groupsuserisin", (data) ->
    groups=data.groups
    cback(groups)



# #BUG: make backbone views for all of this
# postable_members_template = renderable (fqpn, users, owner, scmode=false) ->
#   if owner is 'True'
#     if scmode
#       userlist= (k for k,v of users)
#       w.one_col_table "Users", userlist
#     else
#       #w.table_from_dict("User", "Can User Write", users)
#       # v=PostableMembersView({$e_el:$e, fqpn:fqpn, users:users})
#       # return v.render()
#       views=(new RWToggleView({rwmode:users[u], fqpn:fqpn, memberable:u}) for u of users)
#       rendered = (v.render().el for v in views)
#       #console.log "RENDER1", rendered
#       #console.log "RENDER2"
#       $widget=w.$one_col_table("User", rendered)
#   else
#     userlist= (k for k,v of users)
#     w.inline_list userlist
rwmap = (boolrw) ->
    if boolrw==true
        return "read and post"
    else
        return "read only"

postable_inviteds_template = renderable (fqpn, users, scmode=false) ->
  #console.log "USERS", users
  userlist= (v[0] for k,v of users)
  if scmode
    userlist= (v[0] for k,v of users)
    if userlist.length == 0
      userlist = ['No Invitations Yet']
    #console.log "USERLIST", userlist
    w.one_col_table "Invited Users", userlist
  else
    if userlist.length == 0
      users={'No Invitations Yet': ['No Invitations Yet','']}
    #console.log users
    namedict={}
    for k of users
      #console.log "k is", k
      namedict[users[k][0]]=rwmap(users[k][1])
    #console.log "BANEDICT", namedict, users
    w.table_from_dict("Invited User", "Access", namedict)

# #Bug: these need to become collection Views
# postable_members = (fqpn, owner, data, template, scmode=false) ->
#   template(fqpn, data.users, owner, scmode)

postable_inviteds = (fqpn, data, template, scmode=false) ->
  template(fqpn, data.users, scmode)



postable_info_layout = renderable (isowner, {basic, owner, nick}, oname, cname, mode="filter") ->
  #console.log isowner, basic, owner, nick, oname, cname
  description = basic.description
  if description is ""
    description = "not provided"
  if isowner
    dtext = w.editable_text(description)
  else
    dtext = description

  if mode is "filter"
    modetext = "Link"
  else if mode is "profile"
    modetext = "Info"
  url= "#{prefix}/postable/#{basic.fqin}/#{mode}/html"
  a= "&nbsp;&nbsp;<a href=\"#{url}\">#{basic.name}</a>"
  dl '.dl-horizontal', ->
    dt "Description"
    dd ->
      raw dtext
    #dt "UUID"
    #dd nick
    dt "Owner"
    dd oname
    dt "Creator"
    dd cname
    dt "Created on"
    dd basic.whencreated
    dt "#{modetext}:"
    dd ->
      raw a

postable_info_layout2 = renderable ({basic, owner, nick}, oname, cname, mode="profile") ->
  if mode is "filter"
    modetext = "Link"
  else if mode is "profile"
    modetext = "Info/Admin"
  url= "#{prefix}/postable/#{basic.fqin}/#{mode}/html"
  a= "&nbsp;&nbsp;<a href=\"#{url}\">#{basic.name}</a>"
  dl '.dl-horizontal', ->
    dt "Owner"
    dd oname
    dt "#{modetext}:"
    dd ->
      raw a

library_info_template = renderable (isowner, data) ->
  postable_info_layout isowner, data.library, data.oname, data.cname

group_info_template = renderable (isowner, data) ->
  postable_info_layout isowner, data.group, data.oname, data.cname

library_itemsinfo_template = renderable (isowner, data) ->
  postable_info_layout isowner, data.library, data.oname, data.cname, "profile"

group_itemsinfo_template = renderable (isowner, data) ->
  postable_info_layout isowner, data.group, data.oname, data.cname, "profile"

#controller style stuff should be added here.
postable_info = (isowner, data, template) ->
  template(isowner, data)

#content=widgets.one_submit_with_cb("invite_user","Invite a user using their email:", "Invite", "Can Post?")
#$('div#invitedform').append(content)
#content=widgets.dropdown_submit_with_cb("add_group", ['a','b','c'],"Add a group you are a member of:","Add", "Can Post?")

class InviteUser extends Backbone.View

  tagName: 'div'

  events:
    "click .sub" : "inviteUserEH"

  initialize: (options) ->
    {@withcb, @postable} = options
    if @withcb
      @content=widgets.one_submit_with_cb("Invite a user using their email:", "Invite", "Can Post?")
    else
      @content=widgets.one_submit("Invite a user using their email:", "Invite")

  render: () =>
    @$el.html(@content)
    return this

  inviteUserEH: =>
    loc=window.location
    cback = (data) ->
            #console.log "return data", data, loc
            window.location=location
    eback = (xhr, etext) ->
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert "Did not succeed: #{etext}"
    #console.log("GGG",@$el)
    #default for groups
    changerw=false
    if @withcb
      rwmode=@$('.cb').is(':checked')
      if rwmode
        changerw=true
      else
        changerw=false
    adsid=@$('.txt').val()
    syncs.invite_user(adsid, @postable, changerw, cback, eback)

class MakePublic extends Backbone.View

  tagName: 'div'

  events:
    "click .sub" : "makePublic"

  initialize: (options) ->
    {@postable, @users} = options
    @ispublic=false
    if @users['adsgut/user:anonymouse']?
      @ispublic=true

    if @ispublic
      #console.log "POSTABLE", @postable
      url= "#{prefix}/postable/#{@postable}/filter/html"
      @content="<p><a class='btn btn-info' href='#{url}'>PUBLIC LINK</a></p>"
    else
      @content=widgets.zero_submit("Clicking this will enable anyone to see this library (they cant write to it):", "Make Public")

  render: () =>
    @$el.html(@content)
    return this

  makePublic: =>
    loc=window.location
    #console.log "A"

    cback2 = (data) =>
            #console.log "return data cback2", data, loc
            window.location = location

    cback = (data) =>
            #console.log "return data cback", data, loc, @postable
            syncs.add_group('adsgut/group:public', @postable, false, cback2, eback)

    eback = (xhr, etext) ->
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert "Did not succeed: #{etext}"

    #console.log("GGG")
    syncs.make_public(@postable, cback, eback)

class AddGroup extends Backbone.View

  tagName: 'div'

  events:
    "click .sub" : "addGroupEH"

  initialize: (options) ->
    {@withcb, @postable, @groups} = options
    @groupnames={}
    for g in @groups
      @groupnames[g] = parse_fqin(g)
    if @withcb
      @content=widgets.dropdown_submit_with_cb(@groups, @groupnames, "Add a group you are a member of:","Add", "Can Post?")
    else
      @content=widgets.dropdown_submit(@groups, @groupnames, "Add a group you are a member of:","Add")

  render: () =>
    if @groups.length ==0
      @$el.html(@content)
      @.$(":input").attr("disabled", true)
      @$el.append("<p class='text-error'>You are not a member of any group. Create some groups first.</p>")
    else
      @$el.html(@content)
    return this

  addGroupEH: =>
    loc=window.location
    cback = (data) ->
            #console.log "return data", data, loc
            window.location=location
    eback = (xhr, etext) ->
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert "Did not succeed: #{etext}"
    #console.log("GGG",@$el)
    #default for groups
    changerw=false
    if @withcb
      rwmode=@$('.cb').is(':checked')
      if rwmode
        changerw=true
      else
        changerw=false
    groupchosen=@$('.sel').val()
    #console.log("GC", groupchosen)
    syncs.add_group(groupchosen, @postable, changerw, cback, eback)


class CreatePostable extends Backbone.View

  tagName: 'div'

  events:
    "click .sub" : "createPostableEH"

  initialize: (options) ->
    {@postabletype} = options
    @content=widgets.two_submit("Create a new #{@postabletype}", "Description", "Create")

  render: () =>
    @$el.html(@content)
    return this

  createPostableEH: =>
    loc=window.location
    cback = (data) ->
            #console.log "return data", data, loc
            window.location=location
    eback = (xhr, etext) ->
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert "Did not succeed: #{etext}"
    postable={}
    postable.name=@$('.txt1').val()
    postable.description=@$('.txt2').val()
    syncs.create_postable(postable, @postabletype, cback, eback)

root.get_tags = get_tags
root.get_taggings = get_taggings
#root.format_items = format_items
root.format_item = format_item
root.format_tags = format_tags
root.get_groups= get_groups
root.format_row = format_row
#root.format_stuff = format_stuff
root.format_postings_for_item = format_postings_for_item
root.format_notes_for_item = format_notes_for_item
root.format_tags_for_item = format_tags_for_item
root.views =
  library_info: postable_info
  group_info: postable_info
  postable_inviteds: postable_inviteds
  InviteUser: InviteUser
  MakePublic: MakePublic
  AddGroup: AddGroup
  CreatePostable: CreatePostable
root.templates =
  library_info: library_info_template
  group_info: group_info_template
  library_itemsinfo: library_itemsinfo_template
  group_itemsinfo: group_itemsinfo_template
  postable_inviteds: postable_inviteds_template
