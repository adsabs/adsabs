root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup
w = widgets
prefix = GlobalVariables.ADS_PREFIX+"/adsgut"

update_postings_taggings: () =>
    @postings={}
    console.log("itys", @items)
    itemlist=("items=#{encodeURIComponent(i.basic.fqin)}" for i in @items)
    itemsq=itemlist.join("&")
    $.get prefix+"/items/taggingsandpostings?#{itemsq}", (data)=>
        [@stags, @notes]=get_taggings(data)
        for own k,v of data.postings
            #console.log "2>>>", k,v[0],v[1]
            if v[0] > 0
                @postings[k]=(e.thething.postfqin for e in v[1])
            else
                @postings[k]=[]
        for i in @items
            fqin=i.basic.fqin
            @itemviews[fqin].update(@postings[fqin], @notes[fqin], @stags[fqin])
            @itemviews[fqin].render()

class TagsetView extends Backbone.View
    events:
        "click .tag" : "submitTags"
        "click .done" : "iDone"

    initialize: (options) ->
        {@stags, @$el,  @memberable, @items, @nameable, @itemtype, @loc, @noteform} = options

      


      render: =>
        $lister=@$el
        #$lister.append('<legend>Selected Items</legend>')
        $ctrls=@$('.ctrls')
        @itemviews={}
        for i in @items
            fqin=i.basic.fqin
            ins = 
                stags: @stags[fqin]
                notes: @notes[fqin]
                postings: @postings[fqin]
                item: i
                memberable: @memberable
                noteform: @noteform
            v=new ItemView(ins)
            $lister.append(v.render().el)
            @itemviews[fqin]=v
        # for v in views
        #     $lister.append(v.render().el)
        eback = (xhr, etext) =>
            console.log "ERROR", etext
            #replace by a div alert from bootstrap
            alert 'Did not succeed'
        cback = (data) =>
            console.log data
            libs=_.union(data.libraries, data.groups)
            $ctrls.append(w.postalall_form(@nameable, @itemtype, libs))
        syncs.get_postables_writable(@memberable, cback, eback)
        return this

      iDone: =>
        #loc=window.location
        cback = (data) =>
            #alert(@loc)
            window.location=@loc
        eback = (xhr, etext) =>
            console.log "ERROR", etext, @loc
            #replace by a div alert from bootstrap
            alert 'Did not succeed'
        #if you dont do things, atleast save items
        syncs.save_items(@items, cback, eback)
        #SHOULD HAVE A TAB CLOSE
        window.close()
        return false

      submitPosts: =>
        libs=@$('.multilibrary').val()
        if libs is null
            libs=[]
        postables=libs
        makepublic=@$('.makepublic').is(':checked')
        if makepublic
            postables=postables.concat ['adsgut/group:public']
        loc=window.location
        cback = (data) =>
            #window.location=loc
            @update_postings_taggings()
        eback = (xhr, etext) =>
            console.log "ERROR", etext, loc
            #replace by a div alert from bootstrap
            alert 'Did not succeed'
        syncs.submit_posts(@items, postables, cback, eback)
        return false

      submitTags: =>
        tagstring=@$('.tagsinput').val()
        if tagstring is ""
            console.log "a"
            tags=[]
        else
            console.log "b", (e for e in tagstring.split(','))
            tags=(e.trim() for e in tagstring.split(','))
            tags=(e for e in tags when e != "")
        loc=window.location
        cback = (data) =>
            #window.location=loc
            @$('.tagsinput').val("")
            @update_postings_taggings()
        eback = (xhr, etext) =>
            console.log "ERROR", etext, loc
            #replace by a div alert from bootstrap
            alert 'Did not succeed'
        syncs.submit_tags(@items, tags, cback, eback)
        return false

root.tpsets=
    TagsetView: TagsetView

