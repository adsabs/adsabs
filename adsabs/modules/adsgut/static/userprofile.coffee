#we'll start with user profile funcs
root = exports ? this
$=jQuery
console.log "In userprofile"
h = teacup
w = widgets
prefix = GlobalVariables.ADS_PREFIX+"/adsgut"

parse_fqin = (fqin) -> 
    vals=fqin.split(':')
    return vals[-1+vals.length]

parse_userinfo = (data) ->
    publ= "adsgut/group:public"
    priv= data.user.nick+"/group:default"
    postablesin=[]
    postablesowned=data.user.postablesowned
    powfqin=(p.fqpn for p in postablesowned)
    pinfqin=(p.fqpn for p in data.user.postablesin)
    pinfqin=_.difference(pinfqin, powfqin)
    for p in data.user.postablesin
        if p.fqpn in pinfqin
            postablesin.push(p)
    postablesinvitedto=data.user.postablesinvitedto
    groupsin = (e for e in postablesin when e.ptype is 'group' and e.fqpn not in [publ, priv])
    groupsowned = (e for e in postablesowned when e.ptype is 'group' and e.fqpn not in [publ, priv])
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

    librariesin = _.union((e for e in postablesin when e.ptype is 'library'), groupsin)
    librariesowned =  _.union((e for e in postablesowned when e.ptype is 'library'), groupsowned)
    librariesinvitedto = _.union((e for e in postablesinvitedto when e.ptype is 'library'), groupsinvitedto)
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
    for ele in data.postablelibs
        if ele.reason != ''
            ele.reason = " (through #{ele.reason})"
        if ele.fqpn not in powfqin
            userdict.librariesin.push(ele)
    userdict.librariesin = _.union(userdict.librariesin, groupsin)
    return userdict


make_postable_link = h.renderable (fqpn, libmode=false, ownermode=false) ->
    if libmode is "lib"
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            h.text parse_fqin(fqpn)
    else if  libmode is "group"
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            #h.i ".icon-cog"
            #h.raw "&nbsp;"
            h.text parse_fqin(fqpn)
    else
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            h.text parse_fqin(fqpn)


make_postable_link_secondary = h.renderable (fqpn, libmode=false, ownermode=false) ->
    if libmode is "lib"
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            h.i ".icon-cog"
            h.raw "&nbsp;"
            if ownermode
                h.text "admin"
            else
                h.text "info"
    else if  libmode is "group"
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
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
    
    initialize: (options) ->
        @libmode=options.libmode
        @ownermode=options.ownermode

    render: =>

        if @model.get('invite')
            if @libmode=="lib"
                @$el.html(w.table_from_dict_partial_many(parse_fqin(@model.get('fqpn')), [@model.get('description'), @model.get('readwrite'), w.single_button('Yes')]))
            else
                 @$el.html(w.table_from_dict_partial_many(parse_fqin(@model.get('fqpn')), [@model.get('description'), w.single_button('Yes')]))

        else
            #content = w.one_col_table_partial(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode))
            if @libmode=="lib"
                content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)+@model.get('reason'),[@model.get('description'), @model.get('readwrite'), make_postable_link_secondary(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)])
            else
                content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode),[@model.get('description'), make_postable_link_secondary(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode)])

            @$el.html(content)
        return this

    clickedYes: =>
        loc=window.location
        cback = (data) ->
            console.log "return data", data, loc
            window.location=location
        eback = (xhr, etext) ->
            console.log "ERROR", etext, loc
            #replace by a div alert from bootstrap
            alert 'Did not succeed'
        console.log("GGG",@model, @$el)
        useremail=@model.get('email')
        syncs.accept_invitation(useremail, @model.get('fqpn'), cback, eback)



class PostableList extends Backbone.Collection
    
    model: Postable

    initialize: (models, options) ->
        @listtype=options.listtype
        @invite=options.invite
        @nick=options.nick
        @email=options.email

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
        views = (new PostableView(model:m, libmode:@libmode, ownermode:@ownermode) for m in @collection.models)
        rendered = (v.render().el for v in views)
        console.log "RENDER1", rendered
        console.log "RENDER2"
        if @collection.invite
            if views.length == 0
                rendered = ["<td colspan=4>No Invitations</td>"]
            if @libmode=='group'
                $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Description","Accept?"], rendered)
            else if @libmode=='lib'
                $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Description","Access","Accept?"], rendered)

        else
            #$widget=w.$one_col_table(@tmap[@collection.listtype], rendered)
            if views.length == 0
                rendered = ["<td colspan=4>None</td>"]
            if @libmode=='group'
                $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Description", "Manage"], rendered)
            else if @libmode=='lib'
                $widget=w.$table_from_dict_many(lmap[@libmode]+' '+@tmap[@collection.listtype], ["Description", "Access", "Manage"], rendered)
        @$el.append($widget)
        #widgets.decohelp('#useradder', 'help me', 'popover', 'left')
        return this

rwmap = (boolrw) ->
    if boolrw==true
        return "read-write"
    else
        return "read-only"

render_postable = (userdict, plist, $pel, ptype, invite, libmode, ownermode) ->
  plin=new PostableList([],listtype:ptype, invite:invite, nick:userdict.nick, email:userdict.email)
  if libmode=="lib"
    plin.add((new Postable(fqpn:p.fqpn, description: p.description, reason: p.reason, readwrite: rwmap(p.readwrite), invite:plin.invite, nick:plin.nick, email:plin.email) for p in plist))
  else
    plin.add((new Postable(fqpn:p.fqpn, description: p.description, readwrite: rwmap(p.readwrite), invite:plin.invite, nick:plin.nick, email:plin.email) for p in plist))
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
        w.decohelp('.Access', 'true if i can write to the library, false if I can only see it', 'popover', 'top')
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