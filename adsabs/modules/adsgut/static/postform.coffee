root = exports ? this
$=jQuery
#console.log "In Funcs"
h = teacup

do_postform = (sections, config) ->
    {itemstring, itemsInfoURL, itemsTPURL, tagsucwtURL, memberable, itemtype, nam, loc} = config
    {$itemssec} = sections
    $.get "#{tagsucwtURL}?tagtype=ads/tagtype:tag", (data) ->
        #console.log("TUCWT===", itemstring)
        suggestions = data.simpletags
        syncs.post_for_itemsinfo itemsInfoURL, itemstring, (data) ->
            theitems=data.items
            thecount=data.count
            itemlist=(i.basic.fqin for i in theitems)
            itemsq=itemlist.join("&")

            #$.get "#{config.itemsTPURL}?#{itemsq}", (data)->
            syncs.taggings_postings_post_get itemlist, 'none', (data) ->
                [stags, notes]=get_taggings(data)
                postings={}
                for own k,v of data.postings
                    if v[0] > 0
                        postings[k]=([e.posting.postfqin,e.posting.postedby] for e in v[1])
                    else
                        postings[k]=[]
                ido=
                    stags:stags
                    postings:postings
                    notes:notes
                    $el:$itemssec
                    items: theitems
                    noteform: false
                    nameable: nam
                    itemtype:itemtype
                    memberable:memberable
                    loc: loc
                    suggestions: suggestions
                    pview: 'none'
                if thecount == 1
                    ido.noteform=true
                plinv=new itemsdo.ItemsView(ido)
                plinv.render()
                #possible A&A issue
                eb = (err) ->
                    #console.log("ERR", err)
                    for d in theitems
                        format_item(plinv.itemviews[d.basic.fqin].$('.searchresultl'),d)
                cb = (data) ->
                    #console.log "CBDATA", JSON.stringify(data), data.response.docs
                    thedocs = {}
                    for d in data.response.docs
                        thedocs[d.bibcode]=d
                    docnames = (d.bibcode for d in data.response.docs)
                    for d in theitems
                        if d.basic.name in docnames
                            e=thedocs[d.basic.name]
                        else
                            e={}
                        format_item(plinv.itemviews[d.basic.fqin].$('.searchresultl'),e)
                #console.log "ITTYS", theitems
                syncs.send_bibcodes(config.bq1url, theitems, cb, eb)

root.postform = 
    do_postform: do_postform