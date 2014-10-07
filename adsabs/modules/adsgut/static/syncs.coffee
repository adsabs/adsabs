###
the idea behind syncs.coffee is to create a place where all communication with the server is handled
it might be possible to throw this into a Backbone.sync structure where we do CRUD at the level
of the library (rather than at the level of individual items)
###

#set up globals
root = exports ? this
$=jQuery
h = teacup
doajax=$.ajax
#Get the Beer prefix, append adsgut to it
prefix = GlobalVariables.ADS_PREFIX+"/adsgut"

#send params simply sends a JSON dictionary 'data' as a POST request to 'url'
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

#This does a GET to a 'url'
do_get = (url, cback, eback) ->
    params=
        type:'GET'
        dataType:'json'
        url:url
        success:cback
        error:eback
    xhr=doajax(params)

#This function is used to send a list of bibcodes
#to bigquery. The standard URL for bigquery is PREFIX+'/adsgut/bigquery/bibcodes'
send_bibcodes = (url, items, cback, eback) ->
    #bibcodes = (encodeURIComponent(i.basic.name) for i in items)
    bibcodes = (i.basic.name for i in items)
    data =
        bibcode : bibcodes
    send_params(url, data, cback, eback)


#This method changes ownership of a group or library. You must supply the 'adsid', or
#the email of the user, and the fqpn (fully qualified name(fqin)) of the group or library being changed
#currently this is only used by libraries
change_ownership = (adsid, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:adsid
        op:'changeowner'
    send_params(url, data, cback, eback)

#for a given library with fqin 'fqpn', change whether a group or user with fqin 'fqmn'
#can post into the library. Its a toggle: if the current status is read-only, the status will become
#read-write
toggle_rw = (fqmn, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:fqmn
        op:'togglerw'
    send_params(url, data, cback, eback)

#Change description of library to text 'description'. Why is there
#a memberable 'crap' here? TODO
change_description = (description, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:"crap"
        op:'description'
        description:description
    send_params(url, data, cback, eback)

#A user with adsid 'adsid' (email) accepts an invitation to library `fqpn`
accept_invitation = (adsid, fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:adsid
        op:'accept'
    send_params(url, data, cback, eback)

#Invite a user with email 'adsid' to library `fqpn` with a command to change read-only mode true
#or false. The default mode for a user is read-only, so setting this to true changes the mode to read-write
invite_user = (adsid, fqpn, changerw, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/changes"
    data=
        memberable:adsid
        op:'invite'
        changerw:changerw
    send_params(url, data, cback, eback)

#TODO: check if we explicitly pass useras below?
#create a library or a group with a dictionary 'postable'
#this dictionary must have keys 'name' and description'
#also provide 'postabletype' library or group
create_postable = (postable, postabletype, cback, eback) ->
    url= prefix+"/#{postabletype}"
    data=
        name:postable.name
        description:postable.description
    send_params(url, data, cback, eback)

#add a group with fqin 'selectedgroup' as a member of a library 'fqpn'
add_group = (selectedgrp, fqpn, changerw, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/members"
    data=
        member: selectedgrp
        changerw: changerw
    send_params(url, data, cback, eback)

#make a library 'fqpn' public. This involves adding the user anonymouse as a member.
make_public = (fqpn, cback, eback) ->
    url= prefix+"/postable/"+fqpn+"/members"
    data=
        member: 'adsgut/user:anonymouse'
        changerw: false
    send_params(url, data, cback, eback)

#This one is not particularly useful and dosent seem to be used
#DONT USE IT. NOT DOCUMENTED
get_postables = (user, cback, eback) ->
    #bug:possibly buggy split
    #ary=user.split(':')
    #nick=ary[ary.length-1]
    nick=user
    url= prefix+"/user/"+nick+"/postablesuserisin"
    do_get(url, cback, eback)

#For a user, get the libraries you can access. The 'writable' is a misnomer
#we include read-only libraries. This is the CRITICAL method, which can be used to
#bootstrap to get all the users libraries in bumblebee.
get_postables_writable = (user, cback, eback) ->
    #bug:possibly buggy split
    #ary=user.split(':')
    #nick=ary[ary.length-1]
    nick=user
    url= prefix+"/user/"+nick+"/postablesusercanwriteto"
    do_get(url, cback, eback)

#Takes an 'item' fqin, and also the 'itemname'(yes this repetition is bad)
#takes a 'notetuple':[notetext,tagmode] and a context 'ctxt' and posts the note
#The context is usually the fqpn of the library in whose context we are posting this,
#but it can also be 'udg', the personal library, 'public', the publuc library
#not implemented yet, or 'none', which refers to the context of making notes on
#search results. The tagmode reflects exactly this ctxt with '0' for promiscuous, '1' for
#private, 'fqpn' elsewise. Here though promiscuous means go everywhere.
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
    if ctxt not in ['udg','pub','none']
        data.fqpn = ctxt
    if notetuple[0] != ""
        send_params(url, data, cback, eback)

#Takes an 'item' fqin, and also the 'itemname'(yes this repetition is bad)
#takes a tag fqin and a context 'pview' and posts the tag
#The pview is usually the fqpn of the library in whose context we are posting this,
#but it can also be 'udg', the personal library, 'public', the publuc library
#not implemented yet, or 'none', which refers to the context of making notes on
#search results. The tagmode reflects exactly this ctxt.
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
        tagmode = '0'#why is this '0'. Shouldnt it be '1'?is it because of where we weant tags to be seen?
    else
        tagmode = pview
    ts={}
    ts[itemname] = [{name: tag, tagtype:tagtype, tagmode:tagmode}]
    data=
        tagspecs: ts
        itemtype:itemtype
    if tag != ""
        send_params(url, data, cback, eback)

#remove a note from a library. Needs both tagname and fqtn.
#in our UI, the fqtn's uuid is stored in the tags.
#the ctxt can be the public library or a given library
#TODO: if its neither, there is no fqpn, and what happens?

remove_note = (item, tagname, fqtn, ctxt, cback, eback) ->
    tagtype= "ads/tagtype:note"
    url= prefix+"/tagsremove/"+item
    data=
        tagtype: tagtype
        tagname: tagname
    if fqtn!=undefined
        #console.log "FQTN IS", fqtn
        data.fqtn = fqtn
    if ctxt not in ['udg', 'none']
        data.fqpn = ctxt
    if ctxt=='public'
        data.fqpn = "adsgut/library:public"
    send_params(url, data, cback, eback)

#remove a tag from a library. Needs both tagname and fqtn.
#the ctxt can be the public library or a given library
#TODO: if its neither, there is no fqpn, and what happens?

remove_tagging = (item, tagname, fqtn, ctxt, cback, eback) ->
    tagtype= "ads/tagtype:tag"
    url= prefix+"/tagsremove/"+item
    data=
        tagtype: tagtype
        tagname: tagname
    if fqtn!=undefined
        #console.log "FQTN IS", fqtn
        data.fqtn = fqtn
    #console.log "ctxt is", ctxt
    if ctxt not in ['udg', 'none']
        data.fqpn = ctxt
    if ctxt=='public'
        data.fqpn = "adsgut/library:public"
    send_params(url, data, cback, eback)

#remove items from a library. each item in the list is the fqin
#ctxt is the library, or public. If its 'udg' or 'none', what happens?
remove_items_from_postable = (items, ctxt, cback, eback) ->
    url= prefix+"/itemsremove"
    data=
        items: items
    if ctxt not in ['udg', 'none']
        data.fqpn = ctxt
    if ctxt=='public'
        data.fqpn = "adsgut/library:public"
    send_params(url, data, cback, eback)


#the next two are similar to submit_tag and submit_note, but boxcar on
#multiple item fqins, tag names, and library fqpns. In both these you must
#have actual postables. And thus no other tagmodes are allowed, simplifying things.
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

#similar to earlier, multiple items in multiple libraries
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

#just save items, which basically adds to udg
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

#get taggings and postings for item fqins in a library using POST
#we do POST so as to allow very long item strings.
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

#this is a very stupid POST based function which gets basic info for items, given a string of
#colon separated item fqins. It will eventually be removed. Currently its used in the
#exporting form to get some information to draw the page from the stuff given by the
#export
post_for_itemsinfo = (url, itemstring, cback) ->
    eback = () ->
        alert "Error Occurred"
    data =
        items:itemstring
    send_params(url, data, cback, eback)

#removes a user or group using fqin from a library, or a user from a group.
#The memberable is the former fqin, the membable is the latter
remove_memberable_from_membable = (memberable, membable, cback, eback) ->
    url= prefix+"/memberremove"
    data=
        fqpn: membable
        member: memberable
    send_params(url, data, cback, eback)

#deletes a library or a group with fqin membable
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
