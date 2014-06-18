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
#console.log "In Funcs"
h = teacup
doajax=$.ajax
prefix = GlobalVariables.ADS_PREFIX+"/adsgut"
send_params = (url, data, cback, eback) ->
    stringydata = JSON.stringify(data)
    params=
        type:'POST'
        dataType:'json'
        url:url
        data: stringydata
        contentType: "application/json"
        success:cback
        error:eback
    xhr=doajax(params)

# import requests

# rstr="bibcode\n2013MPEC....H...46."

# headers = {'Content-Type': 'big-query/csv'}
# url='http://localhost:9002/solr/collection1/select'
# qdict = {
#     'q':'text:*:*',
#     'fq':'{!bitset compression=none}',
#     'wt':'json',
#     'fl':'title,year,author'
# }
# r = requests.post(url, params=qdict, data=rstr, headers=headers)
# print r.url
# print r.text

send_bibcodes = (url, items, cback, eback) ->
    #bibcodes = (encodeURIComponent(i.basic.name) for i in items)
    bibcodes = (i.basic.name for i in items)
    data =
        bibcode : bibcodes
    #console.log "SBDATA", data
    send_params(url, data, cback, eback)


do_get = (url, cback, eback) ->
    params=
        type:'GET'
        dataType:'json'
        url:url
        success:cback
        error:eback
    xhr=doajax(params)

change_ownership = (adsid, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:adsid
        op:'changeowner'
    send_params(url, data, cback, eback)

toggle_rw = (fqmn, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:fqmn
        op:'togglerw'
    send_params(url, data, cback, eback)

change_description = (description, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:"crap"
        op:'description'
        description:description
    send_params(url, data, cback, eback)

accept_invitation = (adsid, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:adsid
        op:'accept'
    send_params(url, data, cback, eback)

invite_user = (adsid, postable, changerw, cback, eback) ->
    url= prefix+"/postable/"+postable+"/changes"
    data=
        memberable:adsid
        op:'invite'
        changerw:changerw
    send_params(url, data, cback, eback)

#BUG: should we explicitly pass useras below?
create_postable = (postable, postabletype, cback, eback) ->
    url= prefix+"/#{postabletype}"
    data=
        name:postable.name
        description:postable.description
    send_params(url, data, cback, eback)

add_group = (selectedgrp, postable, changerw, cback, eback) ->
    url= prefix+"/postable/"+postable+"/members"
    data=
        member: selectedgrp
        changerw: changerw
    #console.log "DATA", data
    send_params(url, data, cback, eback)

make_public = (postable, cback, eback) ->
    url= prefix+"/postable/"+postable+"/members"
    data=
        member: 'adsgut/user:anonymouse'
        changerw: false
    #console.log "make public"
    send_params(url, data, cback, eback)

#This one is not particularly useful and dosent seem to be used
get_postables = (user, cback, eback) ->
    #bug:possibly buggy split
    #ary=user.split(':')
    #nick=ary[ary.length-1]
    nick=user
    url= prefix+"/user/"+nick+"/postablesuserisin"
    do_get(url, cback, eback)

get_postables_writable = (user, cback, eback) ->
    #bug:possibly buggy split
    #ary=user.split(':')
    #nick=ary[ary.length-1]
    nick=user
    url= prefix+"/user/"+nick+"/postablesusercanwriteto"
    do_get(url, cback, eback)

submit_note = (item, itemname, notetuple, ctxt, cback, eback) ->
    tagtype= "ads/tagtype:note"
    itemtype= "ads/itemtype:pub"
    url= prefix+"/tags/"+item
    ts={}
    ts[itemname] = [{content:notetuple[0], tagtype:tagtype, tagmode:notetuple[1]}]
    #console.log "whee", ts, notetuple
    data=
        tagspecs: ts
        itemtype:itemtype
    if ctxt not in ['udg','public','none']
        data.fqpn = ctxt
    if notetuple[0] != ""
        send_params(url, data, cback, eback)

submit_tag = (item, itemname, tag, pview, cback, eback) ->
    tagtype= "ads/tagtype:tag"
    itemtype= "ads/itemtype:pub"
    url= prefix+"/tags/"+item
    tagmode = '1'
    if pview is 'pub'
        #additionally, item must be made public. should public also mean all groups item is in
        #as now. YES.
        tagmode = '0'
    else if pview is 'udg' or pview is 'none'
        tagmode = '0'
    else
        tagmode = pview
    ts={}
    ts[itemname] = [{name: tag, tagtype:tagtype, tagmode:tagmode}]
    data=
        tagspecs: ts
        itemtype:itemtype
    if tag != ""
        send_params(url, data, cback, eback)

remove_note = (item, tagname, ctxt, cback, eback) ->
    tagtype= "ads/tagtype:note"
    url= prefix+"/tagsremove/"+item
    data=
        tagtype: tagtype
        tagname: tagname
    if ctxt not in ['udg', 'none']
        data.fqpn = ctxt
    if ctxt=='public'
        data.fqpn = "adsgut/library:public"
    send_params(url, data, cback, eback)

remove_tagging = (item, tagname, fqtn, ctxt, cback, eback) ->
    tagtype= "ads/tagtype:tag"
    url= prefix+"/tagsremove/"+item
    data=
        tagtype: tagtype
        tagname: tagname
    if fqtn!=undefined
        console.log "FQTN IS", fqtn
        data.fqtn = fqtn
    #console.log "ctxt is", ctxt
    if ctxt not in ['udg', 'none']
        data.fqpn = ctxt
    if ctxt=='public'
        data.fqpn = "adsgut/library:public"
    send_params(url, data, cback, eback)

remove_items_from_postable = (items, ctxt, cback, eback) ->
    url= prefix+"/itemsremove"
    data=
        items: items
    if ctxt not in ['udg', 'none']
        data.fqpn = ctxt
    if ctxt=='public'
        data.fqpn = "adsgut/library:public"
    send_params(url, data, cback, eback)

submit_tags = (items, tags, postables, cback, eback) ->
    tagtype= "ads/tagtype:tag"
    itemtype= "ads/itemtype:pub"
    url= prefix+"/items/taggings"
    #console.log "TAGS ARE", tags,"EFFIN POSTS",postables
    ts={}
    inames=[]
    for i in items
        fqin=i.basic.fqin
        name=i.basic.name
        if tags[fqin].length > 0
            inames.push(name)
            ts[name]=[]
            for t in tags[fqin]
              if postables.length > 0
                for p in postables
                  ts[name].push({name:t, tagtype:tagtype, tagmode:p})
              else
                  ts[name].push({name:t, tagtype:tagtype})
    if inames.length >0
        data=
            tagspecs: ts
            itemtype:itemtype
            items:inames
        send_params(url, data, cback, eback)
    else
        cback()

submit_notes = (items, notetuples, cback, eback) ->
    tagtype= "ads/tagtype:note"
    itemtype= "ads/itemtype:pub"
    url= prefix+"/items/taggings"
    ts={}
    inames=[]
    for i in items
        fqin=i.basic.fqin
        name=i.basic.name
        if notetuples[fqin].length > 0
            inames.push(name)
            ts[name] = ({content:nt[0], tagtype:tagtype, tagmode:nt[1]} for nt in notetuples[fqin])
    if inames.length >0
        data=
            tagspecs: ts
            itemtype:itemtype
            items:inames
        send_params(url, data, cback, eback)
    else
        cback()

submit_posts = (items, postables, cback, eback) ->
    itemtype= "ads/itemtype:pub"
    #console.log items, '|||', postables
    itemnames= (i.basic.name for i in items)
    url= prefix+"/items/postings"
    if postables.length >0
        data=
            postables:postables
            itemtype:itemtype
            items:itemnames
        send_params(url, data, cback, eback)
    else
        cback()

#there will always be items so no guarding required
save_items = (items, cback, eback) ->
    itemtype= "ads/itemtype:pub"
    #console.log items, '|||'
    itemnames= (i.basic.name for i in items)
    url= prefix+"/items"
    data=
        items:itemnames
        itemtype:itemtype
    send_params(url, data, cback, eback)

taggings_postings_post_get = (items, pview, cback) ->
    url= prefix+"/items/taggingsandpostings"
    eback = () ->
        alert "Error Occurred"
    data=
        items:items
    #console.log "PVIEW", pview
    if pview not in ['udg', 'none', 'public']
        data.fqpn = pview
    send_params(url, data, cback, eback)

post_for_itemsinfo = (url, itemstring, cback) ->
    eback = () ->
        alert "Error Occurred"
    data =
        items:itemstring
    send_params(url, data, cback, eback)

remove_memberable_from_membable = (memberable, membable, cback, eback) ->
    url= prefix+"/memberremove"
    data=
        fqpn: membable
        member: memberable
    send_params(url, data, cback, eback)

delete_membable = (membable, cback, eback) ->
    url= prefix+"/membableremove"
    data=
        fqpn: membable
    send_params(url, data, cback, eback)

root.syncs=
    accept_invitation: accept_invitation
    invite_user: invite_user
    add_group: add_group
    make_public: make_public
    change_ownership: change_ownership
    toggle_rw: toggle_rw
    get_postables: get_postables
    get_postables_writable: get_postables_writable
    submit_note:submit_note
    submit_tag:submit_tag
    submit_tags:submit_tags
    submit_notes:submit_notes
    submit_posts:submit_posts
    save_items:save_items
    create_postable: create_postable
    change_description: change_description
    send_bibcodes: send_bibcodes
    taggings_postings_post_get: taggings_postings_post_get
    post_for_itemsinfo: post_for_itemsinfo
    remove_tagging: remove_tagging
    remove_note: remove_note
    remove_items_from_postable: remove_items_from_postable
    remove_memberable_from_membable: remove_memberable_from_membable
    delete_membable: delete_membable
