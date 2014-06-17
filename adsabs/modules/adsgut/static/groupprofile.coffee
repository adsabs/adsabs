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
      "click .removemember" : "removeMember"

    initialize: (options) ->
        {@rwmode, @memberable, @fqpn, @username, @owner, @ownerfqin} = options
        #console.log "PVIN", @rwmode, @memberable, @fqpn

    render: =>
        if not @owner
            content = w.one_col_table_partial(@username)
        else
            if @ownerfqin==@memberable
                content = w.table_from_dict_partial(@username, '')
            else
                content = w.table_from_dict_partial(@username, '<a class="removemember" style="cursor:pointer;"><span class="i badge badge-important">x</span></a>')
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
    #if @owner is true
    #console.log @owner, @ownerfqin, @fqpn
    views=(new PostableView({rwmode:@users[u][1], fqpn:@fqpn, memberable:u, owner: @owner, ownerfqin: @ownerfqin, username:@users[u][0]}) for u of @users)
    rendered = (v.render().el for v in views)
    if not @owner
        $widget=w.$one_col_table("User", rendered)
    else
        $widget=w.$table_from_dict("User", "Remove", rendered)
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

# {{ inviteform.changerw }} <label class="checkbox">Can Post?</label>
get_info = (sections, config) ->

    $.get config.infoURL, (data) ->
        content=views.group_info config.owner, data, templates.group_info
        ownerfqin=data.group.owner
        sections.$infodiv.append(content)
        if config.owner
            make_editable_description(sections.$infodiv, config.fqpn)
        sections.$infodiv.show()

        $.get config.membersURL, (data) ->
            plinv=new PostableListView(users:data.users, fqpn:config.fqpn, owner:config.owner, ownerfqin: ownerfqin, $e_el: sections.$membersdiv)
            plinv.render()
            sections.$membersdiv.show()
            if config.owner
                #view=new views.InviteUser({postable: config.fqpn, withcb:false})
                #sections.$invitedform.append(view.render().$el)
                #sections.$invitedform.show()
                $.get config.invitedsURL, (data) ->
                    content=views.postable_inviteds config.fqpn, data, templates.postable_inviteds, true
                    sections.$invitedsdiv.append(content)
                    sections.$invitedsdiv.show()

    cback = () ->
        window.location=config.postablesURL
    eback = () ->
        alert "An error occurred in deletion"
    $('#postabledeleter').click (e)->
        e.preventDefault()
        syncs.delete_membable(config.fqpn, cback, eback)

root.groupprofile=
    PostableView: PostableView
    PostableListView: PostableListView
    get_info: get_info
