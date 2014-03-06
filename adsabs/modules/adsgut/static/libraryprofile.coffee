#we'll start with user profile funcs
root = exports ? this
$=jQuery
#console.log "In libraryprofile"
h = teacup
w = widgets

rwmap = (boolrw) ->
    if boolrw==true
        return "read and post"
    else
        return "read only"

class PostableView extends Backbone.View

  tagName: "tr"
     
  events:
    "click .yesbtn" : "clickedToggle"

  initialize: (options) ->
    {@rwmode, @memberable, @fqpn, @owner, @username, @ownerfqin} = options
    #console.log "PVIN", @rwmode, @memberable, @fqpn, @username

  render: =>
    #content = w.one_col_table_partial(@memberable)
    #console.log "RWMODE", @rwmode
    if not @owner
        uname = @username
        if @username == 'group:public'
            uname = "All ADS Users"
        if @username == 'anonymouse'    
            uname = "General Public"
        content = w.table_from_dict_partial(uname, "Only owner can see this.")
    else
        if @ownerfqin==@memberable
            content = w.table_from_dict_partial(@username+" (owner)", rwmap(@rwmode))
        else
            uname = @username
            if @username == 'group:public'
                uname = "All ADS Users"

            if @username != 'anonymouse'
                content = w.table_from_dict_partial(uname, w.single_button_label(rwmap(@rwmode), "Toggle"))
            else
                uname = "General Public"
                content = w.table_from_dict_partial(uname, rwmap(@rwmode))
    
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
    #console.log "RENDERING", @owner, @users
    #if @owner is true
    views=(new PostableView({rwmode:@users[u][1], fqpn:@fqpn, memberable:u, username:@users[u][0], owner: @owner, ownerfqin:@ownerfqin}) for u of @users)
    rendered = (v.render().el for v in views)
    #console.log "RENDER1", rendered
    #console.log "RENDER2"
    #$widget=w.$one_col_table("User", rendered)
    $widget=w.$table_from_dict("User", "Access", rendered)
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
        content=views.library_info data, templates.library_info
        ownerfqin=data.library.owner
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
            #console.log "DATA", data
            plinv=new PostableListView(users:data.users, fqpn:config.fqpn, owner:config.owner, ownerfqin: ownerfqin, $e_el: sections.$membersdiv)
            plinv.render()
            sections.$membersdiv.show()
            if config.owner
                #console.log "gaga", config.owner
                viewu=new views.InviteUser({postable: config.fqpn, withcb:true})
                viewp=new views.MakePublic({postable: config.fqpn, users: data.users})
                sections.$makepublicform.append(viewp.render().$el)
                sections.$makepublicform.show()
                $.get config.guiURL, (data) ->
                    groups=data.groups
                    view=new views.AddGroup({postable: config.fqpn, groups:groups, withcb:true} )
                    sections.$invitedform.append(view.render().$el)
                    sections.$invitedform.show()
                    $.get config.invitedsURL, (data) ->
                        content=views.postable_inviteds config.fqpn, data, templates.postable_inviteds, false
                        sections.$invitedsdiv.prepend(viewu.render().el)
                        sections.$invitedsdiv.append(content)
                        sections.$invitedsdiv.show()

root.libraryprofile=
    PostableView: PostableView
    PostableListView: PostableListView
    get_info: get_info