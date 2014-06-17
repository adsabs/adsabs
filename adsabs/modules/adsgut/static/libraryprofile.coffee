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
        "click .removemember" : "removeMember"

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
                content = w.table_from_dict_partial_many(@username+" (owner)", [rwmap(@rwmode),""])
            else
                uname = @username
                if @username == 'group:public'
                    uname = "All ADS Users"

                if @username != 'anonymouse'
                    content = w.table_from_dict_partial_many(uname, [w.single_button_label(rwmap(@rwmode), "Toggle"),'<a class="removemember" style="cursor:pointer;"><span class="i badge badge-important">x</span></a>'])
                else
                    uname = "General Public"
                    content = w.table_from_dict_partial_many(uname, [rwmap(@rwmode),'<a class="removemember" style="cursor:pointer;"><span class="i badge badge-important">x</span></a>'])

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

    removeMember: =>
        #console.log "IN REMOVE NOTE", @pview
        membable=@fqpn
        memberable=@memberable
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
    if not @owner
        $widget=w.$table_from_dict("User", "Access", rendered)
    else
        $widget=w.$table_from_dict_many("User", ["Access", "Remove"], rendered)
    @$el.append($widget)
    # else
    #     userlist= (v[0] for k,v of @users)
    #     @$el.html(w.inline_list userlist)
    return this

make_editable_description = ($infodiv, fqpn) ->
    cback = () ->
        #console.log "cback"
    eback = () ->
        #console.log "eback"
    $.fn.editable.defaults.mode = 'inline'
    $infodiv.find('.edtext').editable(
      type:'textarea'
      rows: 2
      url: (params) ->
        syncs.change_description(params.value,fqpn, cback, eback)
    )
    $infodiv.find('.edclick').click (e) ->
      e.stopPropagation()
      e.preventDefault()
      $infodiv.find('.edtext').editable('toggle')

get_info = (sections, config) ->

    $.get config.infoURL, (data) ->
        content=views.library_info config.owner, data, templates.library_info
        ownerfqin=data.library.owner
        sections.$infodiv.append(content)
        # $.fn.editable.defaults.mode = 'inline'
        # sections.$infodiv.find('.edtext').editable(
        #   type:'textarea'
        #   rows: 2
        #   url: (params) ->
        #     syncs.change_description(params.value,config.fqpn, cback, eback)
        # )
        # sections.$infodiv.find('.edclick').click (e) ->
        #   e.stopPropagation()
        #   e.preventDefault()
        #   sections.$infodiv.find('.edtext').editable('toggle')
        if config.owner
            make_editable_description(sections.$infodiv, config.fqpn)
        sections.$infodiv.show()
        #console.log "USER:", config.useras_nick
        if config.useras_nick != 'anonymouse'
            $.get config.membersURL, (data) ->
                #console.log "DATA", data
                plinv=new PostableListView(users:data.users, fqpn:config.fqpn, owner:config.owner, ownerfqin: ownerfqin, $e_el: sections.$membersdiv)
                plinv.render()
                sections.$membersdiv.show()
                if config.owner
                    #console.log "gaga", config.owner
                    #viewu=new views.InviteUser({postable: config.fqpn, withcb:true})
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
                            #sections.$invitedsdiv.prepend(viewu.render().el)
                            sections.$invitedsdiv.append(content)
                            sections.$invitedsdiv.show()
        else
            sections.$membersdiv.empty().append("<p>Only logged in users can see members!</p>")
            sections.$membersdiv.show()
    #deletion
    cback = () ->
        window.location=config.postablesURL
    eback = () ->
        alert "An error occurred in deletion"
    $('#postabledeleter').click (e)->
        e.preventDefault()
        syncs.delete_membable(config.fqpn, cback, eback)

root.libraryprofile=
    PostableView: PostableView
    PostableListView: PostableListView
    get_info: get_info
