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
    console.log "JJJ",powfqin, pinfqin
    pinfqin=_.difference(pinfqin, powfqin)
    console.log "POSARASTAIN", pinfqin
    for p in data.user.postablesin
        if p.fqpn in pinfqin
            postablesin.push(p)
    postablesinvitedto=data.user.postablesinvitedto
    console.log "POSARASTAIN", postablesin
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
    userdict.librariesin = librariesin
    userdict.librariesowned =  librariesowned
    userdict.librariesinvitedto = librariesinvitedto
        
    console.log "LIBGRPSSIN", userdict.librariesin

    return userdict

make_postable_link = h.renderable (fqpn, libmode=false, ownermode=false) ->
    console.log "FQPN", fqpn
    if libmode is "lib"
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            h.text parse_fqin(fqpn)
        h.raw "&nbsp;("
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            if ownermode
                h.text "admin"
            else
                h.text "info"
        h.raw ")"
    else if  libmode is "group"
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            h.text parse_fqin(fqpn)
        h.raw "&nbsp;("
        h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
            h.text "library"
        h.raw ")"
    else
        h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
            h.text parse_fqin(fqpn)



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
            @$el.html(w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=false), [@model.get('description'), w.single_button('Yes')]))
        else
            #content = w.one_col_table_partial(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode))
            content = w.table_from_dict_partial_many(make_postable_link(@model.get('fqpn'), libmode=@libmode, ownermode=@ownermode),[@model.get('description')])
            console.log "CONTENT", content
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
        in: "In"
        ow: "Owned"
        iv: "Invited"

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
            $widget=w.$table_from_dict_many("Invitations", ["Description","Accept?"], rendered)
        else
            #$widget=w.$one_col_table(@tmap[@collection.listtype], rendered)
            $widget=w.$table_from_dict_many(@tmap[@collection.listtype], ["Description"], rendered)
        @$el.append($widget)
        return this


root.userprofile=
    parse_userinfo: parse_userinfo
    Postable: Postable
    PostableList: PostableList
    PostableListView: PostableListView