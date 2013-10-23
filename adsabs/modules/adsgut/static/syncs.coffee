###
the idea behind syncs.coffee is to create a Backbone sync component for our API.
For this we must identify the models and views across our pages.

The method signature of Backbone.sync is sync(method, model, [options])

method – the CRUD method ("create", "read", "update", or "delete")
model – the model to be saved (or collection to be read)
options – success and error callbacks, and all other jQuery request options

With the default implementation, when Backbone.sync sends up a request to save a model, 
its attributes will be passed, serialized as JSON, and sent in the HTTP body with content-type application/json. 
When returning a JSON response, send down the attributes of the model that have been changed by the server, 
and need to be updated on the client. When responding to a "read" request from a collection (Collection#fetch), 
send down an array of model attribute objects.

Whenever a model or collection begins a sync with the server, a "request" event is emitted. 
If the request completes successfully you'll get a "sync" event, and an "error" event if not.

The sync function may be overriden globally as Backbone.sync, or at a finer-grained level, 
by adding a sync function to a Backbone collection or to an individual model.

#but we shall first start slow, by building in direct jquery functions here, instead of Backbone.sync.
This will document the api as well. We wont start with gets, but remember we want to later put gets inside
collections.fetch

error
Type: Function( jqXHR jqXHR, String textStatus, String errorThrown )
success
Type: Function( PlainObject data, String textStatus, jqXHR jqXHR )
###
root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup
doajax=$.ajax
prefix = "/adsgut"
send_params = (url, data, cback, eback) ->
    params=
        type:'POST'
        dataType:'json'
        url:url
        data:JSON.stringify(data)
        contentType: "application/json"
        success:cback
        error:eback
    xhr=doajax(params)

do_get = (url, cback, eback) ->
    params=
        type:'GET'
        dataType:'json'
        url:url
        success:cback
        error:eback
    xhr=doajax(params)

change_ownership = (fqmn, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:fqmn
        op:'changeowner'
    send_params(url, data, cback, eback)

toggle_rw = (fqmn, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:fqmn
        op:'togglerw'
    send_params(url, data, cback, eback)

accept_invitation = (fqmn, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:fqmn
        op:'accept'
    send_params(url, data, cback, eback)

invite_user = (fqmn, postable, changerw, cback, eback) ->
    url= prefix+"/postable/"+postable+"/changes"
    data=
        memberable:fqmn
        op:'invite'
        changerw:changerw
    send_params(url, data, cback, eback)

add_group = (selectedgrp, postable, changerw, cback, eback) ->
    url= prefix+"/postable/"+postable+"/members"
    data=
        member:selectedgrp
        changerw:changerw
    send_params(url, data, cback, eback)

get_postables = (user, cback, eback) ->
    #bug:possibly buggy split
    #ary=user.split(':')
    #nick=ary[ary.length-1]
    nick=user
    url= prefix+"/user/"+nick+"/postablesuserisin"
    do_get(url, cback, eback)

submit_note = (item, note, cback, eback) ->
    tagtype= "ads/tagtype:note"
    itemtype= "ads/itemtype:pub"
    url= prefix+"/tags/"+item
    data=
        tagspecs:[{content:note, tagtype:tagtype}]
        itemtype:itemtype
    if note != ""
        send_params(url, data, cback, eback)

submit_tags = (items, tags, cback, eback) ->
    tagtype= "ads/tagtype:tag"
    itemtype= "ads/itemtype:pub"
    itemnames= (i.basic.name for i in items)
    url= prefix+"/items/taggings"
    console.log "TAGS ARE", tags
    if tags.length >0
        data=
            tagspecs:({name:tag, tagtype:tagtype} for tag in tags)
            itemtype:itemtype
            items:itemnames
        send_params(url, data, cback, eback)

submit_posts = (items, postables, cback, eback) ->
    itemtype= "ads/itemtype:pub"
    console.log items, '|||'
    itemnames= (i.basic.name for i in items)
    url= prefix+"/items/postings"
    if postables.length >0
        data=
            postables:postables
            itemtype:itemtype
            items:itemnames
        send_params(url, data, cback, eback)

save_items = (items, cback, eback) ->
    itemtype= "ads/itemtype:pub"
    console.log items, '|||'
    itemnames= (i.basic.name for i in items)
    url= prefix+"/items"
    data=
        items:itemnames
        itemtype:itemtype
    send_params(url, data, cback, eback)

root.syncs=
    accept_invitation: accept_invitation
    invite_user: invite_user
    add_group: add_group
    change_ownership: change_ownership
    toggle_rw: toggle_rw
    get_postables: get_postables
    submit_note:submit_note
    submit_tags:submit_tags
    submit_posts:submit_posts
    save_items:save_items



