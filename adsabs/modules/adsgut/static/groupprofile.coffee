#we'll start with user profile funcs
root = exports ? this
$=jQuery
#console.log "In groupprofile"
h = teacup
w = widgets


class PostableView extends Backbone.View

  tagName: "tr"
     
  events:
    "click .yesbtn" : "clickedToggle"

  initialize: (options) ->
    {@rwmode, @memberable, @fqpn, @username} = options
    #console.log "PVIN", @rwmode, @memberable, @fqpn

  render: =>
    content = w.one_col_table_partial(@username)
    #content = w.table_from_dict_partial(@memberable, w.single_button_label(@rwmode, "Toggle"))
    #dahtml= "<td>a</td><td>b</td>"
    #console.log "CONTENT", content, @rwmode, @memberable, @fqpn
    @$el.html(content)
    return this

  clickedToggle: =>
    loc=window.location
    cback = (data) ->
        #console.log "return data", data, loc
        window.location=location
    eback = (xhr, etext) ->
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    #console.log("GGG",@model, @$el)
    syncs.toggle_rw(@memberable, @fqpn, cback, eback)

class PostableListView extends Backbone.View

  initialize: (options) ->
    @$el=options.$e_el
    @fqpn=options.fqpn
    @users=options.users
    @owner=options.owner
    @ownerfqin=options.ownerfqin

  render: =>
    #if @owner is true
    views=(new PostableView({rwmode:@users[u][1], fqpn:@fqpn, memberable:u, username:@users[u][0]}) for u of @users)
    rendered = (v.render().el for v in views)
    $widget=w.$one_col_table("User", rendered)
    #$widget=w.$table_from_dict("User", "Can User/Group Post?", rendered)
    @$el.append($widget)
    # else
    #     userlist= (v[0] for k,v of @users)
    #     @$el.html(w.inline_list userlist)
    return this

get_info = (sections, config) ->
    cback = () ->
        #console.log "cback"
    eback = () ->
        #console.log "eback" 
    $.get config.infoURL, (data) ->
        content=views.group_info data, templates.group_info
        ownerfqin=data.group.owner
        sections.$infodiv.append(content)
        $.fn.editable.defaults.mode = 'inline'
        sections.$infodiv.find('.edtext').editable(
          type:'textarea'
          rows: 2
          url: (params) ->
            syncs.change_description(params.value,config.fqpn, cback, eback)
        )
        sections.$infodiv.find('.edclick').click (e) ->
          e.stopPropagation()
          e.preventDefault()
          sections.$infodiv.find('.edtext').editable('toggle')
        sections.$infodiv.show()

        $.get config.membersURL, (data) ->
            plinv=new PostableListView(users:data.users, fqpn:config.fqpn, owner:config.owner, ownerfqin: ownerfqin, $e_el: sections.$membersdiv)
            plinv.render()
            sections.$membersdiv.show()
            if config.owner
                view=new views.InviteUser({postable: config.fqpn, withcb:false})
                sections.$invitedform.append(view.render().$el)
                sections.$invitedform.show()
                $.get config.invitedsURL, (data) ->
                    content=views.postable_inviteds config.fqpn, data, templates.postable_inviteds, true
                    sections.$invitedsdiv.append(content)
                    sections.$invitedsdiv.show()

root.groupprofile=
    PostableView: PostableView
    PostableListView: PostableListView
    get_info: get_info