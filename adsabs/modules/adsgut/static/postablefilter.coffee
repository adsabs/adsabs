root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup

do_postable_info = (sections, config, ptype) ->
    $.get config.infoURL, (data) ->
        if ptype=='library'
            content=views.library_info data, templates.library_itemsinfo
        else if ptype=='group'
            content=views.group_info data, templates.group_itemsinfo
        
        sections.$info.append(content+'<hr/>')
        sections.$info.show()

do_postable_filter = (sections, config) ->
    $.get config.tagsPURL, (data) ->
        for own k,v of data.tags
            format_tags(k, sections.$tagssec, get_tags(v, config.tqtype), config.tqtype)
    $.get config.itemsPURL, (data) ->
        theitems=data.items
        thecount=data.count
        itemlist=("items=#{encodeURIComponent(i.basic.fqin)}" for i in theitems)
        itemsq=itemlist.join("&")
        $.get "#{config.itPURL}?#{itemsq}", (data)->
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
                $el:sections.$items
                items: theitems
                noteform: true
                nameable: false
                itemtype:'ads/pub'
                memberable:config.memberable

            plinv=new itemsdo.ItemsFilterView(ido)
            plinv.render()
    loc = config.loc
    nonqloc=loc.href.split('?')[0]
    if sections.$ua.attr('data') is 'off'
        if nonqloc is loc.href
            urla=loc+"?userthere=true"
        else
            urla=loc+"&userthere=true"
        sections.$ua.attr('href', urla)
        sections.$ua.attr('data', 'on')

root.postablefilter = 
    do_postable_info: do_postable_info
    do_postable_filter: do_postable_filter