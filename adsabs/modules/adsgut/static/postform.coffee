root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup

do_postform = (sections, config) ->
    {itemsInfoURL, itemsTPURL, memberable, itemtype, nam, loc} = config
    {$itemssec} = sections
    $.get itemsInfoURL, (data) ->
        theitems=data.items
        thecount=data.count
        itemlist=("items=#{encodeURIComponent(i.basic.fqin)}" for i in theitems)
        itemsq=itemlist.join("&")
        console.log "ITEMSQAA", theitems, itemlist

        $.get "#{config.itemsTPURL}?#{itemsq}", (data)->
            [stags, notes]=get_taggings(data)
            postings={}
            for own k,v of data.postings
                if v[0] > 0
                    postings[k]=(e.thething.postfqin for e in v[1])
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

            if thecount == 1
                ido.noteform=true
            plinv=new itemsdo.ItemsView(ido)
            plinv.render()

root.postform = 
    do_postform: do_postform