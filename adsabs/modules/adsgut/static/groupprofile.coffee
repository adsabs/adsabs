#we'll start with user profile funcs
root = exports ? this
$=jQuery
console.log "In groupprofile"
h = teacup
w = widgets


class PostableView extends Backbone.View

  tagName: "tr"
     
  events:
    "click .yesbtn" : "clickedToggle"

  initialize: (options) ->
    {@rwmode, @memberable, @fqpn} = options
    console.log "PVIN", @rwmode, @memberable, @fqpn

  render: =>
    content = w.one_col_table_partial(@memberable)
    #content = w.table_from_dict_partial(@memberable, w.single_button_label(@rwmode, "Toggle"))
    #dahtml= "<td>a</td><td>b</td>"
    console.log "CONTENT", content, @rwmode, @memberable, @fqpn
    @$el.html(content)
    return this

  clickedToggle: =>
    loc=window.location
    cback = (data) ->
        console.log "return data", data, loc
        window.location=location
    eback = (xhr, etext) ->
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    console.log("GGG",@model, @$el)
    syncs.toggle_rw(@memberable, @fqpn, cback, eback)

class PostableListView extends Backbone.View

  initialize: (options) ->
    @$el=options.$e_el
    @fqpn=options.fqpn
    @users=options.users
    @owner=options.owner

  render: =>
    if @owner is 'True'
        views=(new PostableView({rwmode:@users[u], fqpn:@fqpn, memberable:u}) for u of @users)
        rendered = (v.render().el for v in views)
        $widget=w.$one_col_table("User", rendered)
        #$widget=w.$table_from_dict("User", "Can User/Group Post?", rendered)
        @$el.append($widget)
    else
        userlist= (k for k,v of @users)
        @$el.html(w.inline_list userlist)
    return this


root.groupprofile=
    PostableView: PostableView
    PostableListView: PostableListView