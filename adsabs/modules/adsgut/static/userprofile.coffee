#we'll start with user profile funcs
root = exports ? this
$=jQuery
console.log "In userprofile"
h = teacup
w = widgets
prefix = "/adsgut"

parse_userinfo = (data) ->
    publ= "adsgut/group:public"
    priv= data.user.nick+"/group:default"
    postablesin=data.user.postablesin
    postablesowned=data.user.postablesowned
    postablesinvitedto=data.user.postablesinvitedto

    userdict=
        groupsin: (e.fqpn for e in postablesin when e.ptype is 'group' and e.fqpn not in [publ, priv])
        groupsowned: (e.fqpn for e in postablesowned when e.ptype is 'group' and e.fqpn not in [publ, priv])
        groupsinvitedto: (e.fqpn for e in postablesinvitedto when e.ptype is 'group')
        librariesin: (e.fqpn for e in postablesin when e.ptype is 'library')
        librariesowned: (e.fqpn for e in postablesowned when e.ptype is 'library')
        librariesinvitedto: (e.fqpn for e in postablesinvitedto when e.ptype is 'library')
        userinfo:
            nick: data.user.nick
            whenjoined: data.user.basic.whencreated
            name: data.user.basic.name
    return userdict

make_postable_link = h.renderable (fqpn) ->
    h.a href:prefix+"/postable/#{fqpn}/profile/html", ->
        h.text fqpn
    h.raw "&nbsp;("
    h.a href:prefix+"/postable/#{fqpn}/filter/html", ->
        h.text "items"
    h.raw ")"

class Postable extends Backbone.Model


class PostableView extends Backbone.View

    tagName: "tr"
       
    events:
        "click .yesbtn" : "clickedYes"
    
    render: =>

        if @model.get('invite')
            @$el.html(w.table_from_dict_partial(@model.get('fqpn'), w.single_button('Yes')))
        else
            content=w.one_col_table_partial(make_postable_link(@model.get('fqpn')))
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
        usernick=@model.get('nick')
        syncs.accept_invitation("adsgut/user:#{usernick}", @model.get('fqpn'), cback, eback)



class PostableList extends Backbone.Collection
    
    model: Postable

    initialize: (models, options) ->
        @listtype=options.listtype
        @invite=options.invite
        @nick=options.nick

#BUG: do we not need to destroy when we move things around?
#also invite isnt enough to have the event based interplay between 2 lists
class PostableListView extends Backbone.View
    tmap:
        in: "In"
        ow: "Owned"
        iv: "Invited"

    initialize: (options) ->
        @$el=options.$e_el

    render: =>
        views = (new PostableView(model:m) for m in @collection.models)
        rendered = (v.render().el for v in views)
        console.log "RENDER1", rendered
        console.log "RENDER2"
        if @collection.invite
            $widget=w.$table_from_dict("Invitations", "Accept?", rendered)
        else
            $widget=w.$one_col_table(@tmap[@collection.listtype], rendered)
        @$el.append($widget)
        return this


root.userprofile=
    parse_userinfo: parse_userinfo
    Postable: Postable
    PostableList: PostableList
    PostableListView: PostableListView