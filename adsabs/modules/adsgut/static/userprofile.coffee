#we'll start with user profile funcs
root = exports ? this
$=jQuery
#console.log "In userprofile"
h = teacup
w = widgets
prefix = GlobalVariables.ADS_PREFIX+"/adsgut"

parse_fqin = (fqin) ->
    vals=fqin.split(':')
    return vals[-1+vals.length]

parse_userinfo = (data) ->
    #console.log "DATA", data
    publicgroup= "adsgut/group:public"
    #privategroup= data.user.nick+"/group:default"
    publiclib= "adsgut/library:public"
    privatelib= data.user.nick+"/library:default"
    postablesin=[]
    postablesowned=data.user.postablesowned
    powfqin=(p.fqpn for p in postablesowned)
    pinfqin=(p.fqpn for p in data.user.postablesin)
    pinfqin=_.difference(pinfqin, powfqin)
    for p in data.user.postablesin
        if p.fqpn in pinfqin
            postablesin.push(p)
    postablesinvitedto=data.user.postablesinvitedto
    groupsin = (e for e in postablesin when e.ptype is 'group' and e.fqpn not in [publicgroup])
    groupsowned = (e for e in postablesowned when e.ptype is 'group' and e.fqpn not in [publicgroup])
    groupsinvitedto = (e for e in postablesinvitedto when e.ptype is 'group')
    userdict=
        groupsin: groupsin
        groupsowned: groupsowned
        groupsinvitedto: groupsinvitedto
        userinfo:
            nick: data.user.nick
            email: data.user.adsid
            whenjoined: data.user.basic.whencreated
            name: data.user.basic.name

    librariesin = (e for e in postablesin when e.ptype is 'library'  and e.fqpn not in [publiclib, privatelib])
    librariesowned =  (e for e in postablesowned when e.ptype is 'library'  and e.fqpn not in [publiclib, privatelib])
    librariesinvitedto = (e for e in postablesinvitedto when e.ptype is 'library'  and e.fqpn not in [publiclib, privatelib])
    for ele in librariesin
        ele.reason = ''
    for ele in groupsin
        ele.reason = ''
    for ele in librariesowned
        ele.reason = ''
    for ele in librariesinvitedto
        ele.reason = ''
    #userdict.librariesin = librariesin
    userdict.librariesowned =  librariesowned
    userdict.librariesinvitedto = librariesinvitedto
    userdict.librariesin = []
    #console.log "powfqin", powfqin
    for ele in data.postablelibs
        if ele.reason != ''
            ele.reason = " (through #{ele.reason})"
        #remove those that our public. if they are not eliminate those owned by me
        if ele.reason!=" (through group:public)" and ele.fqpn not in powfqin
            userdict.librariesin.push(ele)
    #userdict.librariesin = _.union(userdict.librariesin, groupsin)
    #console.log "USERDICT", userdict
    return userdict

getlib = (fqin) ->
    vals=fqin.split(':')
    pre=vals[0].split('/')
    return pre[0]+"/library:"+vals[vals.length-1]

getgroup = (fqin) ->
    vals=fqin.split(':')
    pre=vals[0].split('/')
    return pre[0]+"/group:"+vals[vals.length-1]

make_postable_link = h.renderable (fqpn, libmode=false, ownermode=false) ->
    if libmode is "lib"
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            h.text parse_fqin(fqpn)
    else if  libmode is "group"
        h.a href:prefix+"/postable/#{getlib(fqpn)}/filter/html", ->
            #h.i ".icon-cog"
            #h.raw "&nbsp;"
            h.text parse_fqin(fqpn)
    else
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            h.text parse_fqin(fqpn)


make_postable_link_secondary = h.renderable (fqpn, libmode=false, ownermode=false, text=false) ->
    if libmode is "lib"
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            if text
                h.text text
            else
                h.i ".icon-cog"
                h.raw "&nbsp;"
                if ownermode
                    h.text "admin"
                else
                    h.text "info"
    else if libmode is "group"
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            if text
                h.text text
            else
                h.i ".icon-cog"
                h.raw "&nbsp;"
                if ownermode
                    h.text "admin"
                else
                    h.text "info"
    else
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            h.text parse_fqin(fqpn)

lmap =
    lib: 'Libraries'
    group: 'Groups'

class Postable extends Backbone.Model


class PostableView extends Backbone.View

    tagName: "tr"

    events:
        "click .yesbtn" : "clickedYes"
        "click .removemember" : "removeMember"

    initialize: (options) ->
        @libmode=options.libmode
        @ownermode=options.ownermode
        @listtype=options.listtype

    render: =>
        more=""
        if @model.get('librarykind')=='group'
            more=@model.get('librarykind')
            if not @model.get('invite')
                more=make_postable_link_secondary(getgroup(@model.get('fqpn')), libmode=@libmode, ownermode=@ownermode, more)
        if @model.get('islibrarypublic')==true
            more=more+'(Public)'
        if @model.get('invite')
            if @libmode=="lib"
                @$el.html(w.table_from_dict_partial_many(parse_fqin(@model.get('fqpn')), [@model.get('owner'), @model.get('description'), more, @model.get('readwrite'), w.single_button('Yes')]))
            else
                 @$el.html(w.table_from_dict_partial_many(parse_fqin(@model.get('fqpn')), [@model.get('owner'), @model.get('description'), w.single_button('Yes')]))

        else
            #content = w.one_col_table_partial(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode))
            if @libmode=="lib"
                if @listtype=='in'
                    content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)+@model.get('reason'),[@model.get('owner'), @model.get('description'), more, @model.get('readwrite'), make_postable_link_secondary(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode),'<a class="removemember" style="cursor:pointer;"><span class="i badge badge-important">x</span></a>'])
                else
                    content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)+@model.get('reason'),[@model.get('owner'), @model.get('description'), more, @model.get('readwrite'), make_postable_link_secondary(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)])
            else
                if @listtype=='in'
                    content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode),[@model.get('owner'), @model.get('description'), make_postable_link_secondary(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode), '<a class="removemember" style="cursor:pointer;"><span class="i badge badge-important">x</span></a>'])
                else
                    content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode),[@model.get('owner'), @model.get('description'), make_postable_link_secondary(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)])

            @$el.html(content)
        return this

    clickedYes: =>
        loc=window.location
        cback = (data) ->
            #console.log "return data", data, loc
            window.location=location
        eback = (xhr, etext) ->
            #console.log "ERROR", etext, loc
            #replace by a div alert from bootstrap
            alert 'Did not succeed'
        #console.log("GGG",@model, @$el)
        useremail=@model.get('email')
        syncs.accept_invitation(useremail, @model.get('fqpn'), cback, eback)

    removeMember: =>
        #console.log "IN REMOVE NOTE", @model
        membable=@model.get('fqpn')
        memberable=@model.get('fqin')
        #console.log "<<>>", membable, memberable
        loc=window.location
        cback = (data) =>
            #console.log loc
            window.location=loc
        eback = (xhr, etext) =>
            #console.log "ERROR", etext, loc
            #replace by a div alert from bootstrap
            alert 'Did not succeed'

        syncs.remove_memberable_from_membable(memberable, membable, cback, eback)
        return false



class PostableList extends Backbone.Collection

    model: Postable

    initialize: (models, options) ->
        @listtype=options.listtype
        @invite=options.invite
        @nick=options.nick
        @email=options.email
        @fqin=options.fqin

#BUG: do we not need to destroy when we move things around?
#also invite isnt enough to have the event based interplay between 2 lists
class PostableListView extends Backbone.View
    tmap:
        in: "I am in"
        ow: "I own"
        iv: "I am invited to"

    initialize: (options) ->
        @$el=options.$e_el
        @libmode=options.libmode
        @ownermode=options.ownermode

    render: =>
        views = (new PostableView(model:m, libmode:@libmode, ownermode:@ownermode, listtype:@collection.listtype) for m in @collection.models)
        rendered = (v.render().el for v in views)
        #console.log "RENDER1", @collection.listtype, @collection.invite
        if @collection.invite
            if views.length == 0
                rendered = ["<td colspan=6>No Invitations</td>"]
            if @libmode=='group'
                $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Owner", "Description", "Accept?"], rendered)
            else if @libmode=='lib'
                $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Owner", "Description", "More", "Access","Accept?"], rendered)

        else
            #$widget=w.$one_col_table(@tmap[@collection.listtype], rendered)
            if views.length == 0
                #rendered = ["<td colspan=6>None</td>"]
                if @collection.listtype!='in'
                    rendered = ["<td colspan=6>None</td>"]
                else
                    rendered = ["<td colspan=7>None</td>"]
            if @libmode=='group'
                if @collection.listtype!='in'
                    $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Owner", "Description", "Manage"], rendered)
                else
                    $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Owner", "Description", "Manage", "Leave"], rendered)
            else if @libmode=='lib'
                if @collection.listtype!='in'
                    $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Owner", "Description", "More", "Access", "Manage"], rendered)
                else
                    $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Owner", "Description", "More", "Access", "Manage", "Leave"], rendered)

        @$el.append($widget)
        #widgets.decohelp('#useradder', 'help me', 'popover', 'left')
        return this

rwmap = (boolrw) ->
    if boolrw==true
        return "read and post"
    else
        return "read only"

render_postable = (userdict, plist, $pel, ptype, invite, libmode, ownermode) ->
  #console.log "userdict", userdict, "adsgut/user:"+userdict.name
  plin=new PostableList([],listtype:ptype, invite:invite, nick:userdict.nick, email:userdict.email, fqin:"adsgut/user:"+userdict.name)
  if libmode=="lib"
    plin.add((new Postable(fqpn:p.fqpn, owner: p.owner, description: p.description, reason: p.reason, islibrarypublic: p.islibrarypublic, librarykind:p.librarykind, readwrite: rwmap(p.readwrite), invite:plin.invite, nick:plin.nick, email:plin.email, fqin:plin.fqin) for p in plist))
  else
    plin.add((new Postable(fqpn:p.fqpn, owner: p.owner, description: p.description, readwrite: rwmap(p.readwrite), invite:plin.invite, nick:plin.nick, email:plin.email, fqin:plin.fqin) for p in plist))
  plinv=new PostableListView(collection:plin, $e_el:$pel, libmode:libmode, ownermode:ownermode)
  plinv.render()

layout_userprofile = (sections, config, ptype) ->
  {$create, $info, $owned, $in, $invited} = sections
  {userInfoURL, udgHtmlURL} = config
  wordmap =
    lib: "libraries"
    group: "groups"
  wordmap_singular =
    lib: "library"
    group: "group"
  viewl=new views.CreatePostable({postabletype: wordmap_singular[ptype]})
  $create.append(viewl.render().$el)

  $.get userInfoURL, (data) ->
    userdict=parse_userinfo(data)

    #content=widgets.info_layout(userdict.userinfo, name:'Name', email: 'Email', nick:'Nickname', whenjoined:'Joined')
    # if ptype=='lib'
    #     additional =
    #         saved : "<a href=\"#{udgHtmlURL}\">Items</a>"
    #     content=widgets.info_layout(_.extend(userdict.userinfo, additional), name:'Name', email: 'Email', saved: "Saved")
    # else
    #     additional={}
    #     content=widgets.info_layout(userdict.userinfo, name:'Name', email: 'Email')

    # #if ptype=='lib'
    # #    content=content+"<a href=\"#{udgHtmlURL}\">My Saved Items</a>"
    # $info.append(content)
    # $info.show()
    #console.log "USERDICTA==============", userdict


    render_postable(userdict.userinfo, userdict["#{wordmap[ptype]}owned"], $owned, 'ow', false, ptype, true)
    if ptype=='lib'
        #inlist = _.union(userdict["#{wordmap[ptype]}in"], userdict.librariesother)
        inlist = userdict.librariesin
    else
        inlist = userdict["#{wordmap[ptype]}in"]
    render_postable(userdict.userinfo, inlist, $in, 'in', false, ptype, false)
    render_postable(userdict.userinfo, userdict["#{wordmap[ptype]}invitedto"], $invited, 'iv', true, ptype, false)
    if ptype=='lib'
        w.decohelp('.LibrariesIamin', "Others' libraries I have access to due to being in them or due to being in groups that are in them", 'popover', 'left')
        w.decohelp('.LibrariesIown', 'Libraries I have created', 'popover', 'left')
        w.decohelp('.LibrariesIaminvitedto', "Outstanding invitations to join other ADS users' libraries", 'popover', 'left')
        w.decohelp('.Access', '"read and post" if i can post items to the library, "read only" if I can only view items in the library', 'popover', 'top')
    else if ptype=='group'
        w.decohelp('.GroupsIamin', 'Groups owned by others that I am a member of', 'popover', 'left')
        w.decohelp('.GroupsIown', 'Groups I have created', 'popover', 'left')
        w.decohelp('.GroupsIaminvitedto', "Outstanding invitations to join other ADS users' groups", 'popover', 'left')
# viewg=new views.CreatePostable({postabletype: "group"})
#   $('div#creategroups').append(viewg.render().$el)
#   $.get "{{ url_for('adsgut.userInfo', nick=useras.nick) }}", (data) ->
#     userdict=userprofile.parse_userinfo(data)
#     content=widgets.info_layout(userdict.userinfo, name:'Name', email: 'Email', nick:'Nickname', whenjoined:'Joined')
#     $('#userinfo').append(content)
#     $('#userinfo').show()


#     plgrpow=userprofile.render_postable(userdict.userinfo, userdict.groupsowned, $('#groups div.ow'), 'ow', false, "group", true)

#     plgrpin=userprofile.render_postable(userdict.userinfo, userdict.groupsin, $('#groups div.in'), 'in', false, "group", false)
#     plgrpiv=userprofile.render_postable(userdict.userinfo, userdict.groupsinvitedto, $('#groups div.iv'), 'iv', true, "group", false)

root.userprofile=
    layout_userprofile: layout_userprofile
