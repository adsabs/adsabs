#we'll start with user profile funcs
root = exports ? this
$=jQuery
h = teacup
w = widgets
prefix=GlobalVariables.ADS_PREFIX+'/adsgut'
# format_notes_for_item = (fqin, notes) ->
#   t3list=("<span>#{t}</span><br/>" for t in notes[fqin])
#   if t3list.length >0
#     return "<p>Notes:<br/>"+t3list.join("<br/>")+"</p>"
#   else
#     return ""

# format_tags_for_item = (fqin, stags, nick) ->
#   t2list=("<a href=\"/postable/#{nick}/group:default/filter/html?query=tagname:#{t[0]}&query=tagtype:#{t[1]}\">#{t[0]}</a>" for t in stags[fqin])
#   if t2list.length >0
#     return "<span>Tagged as "+t2list.join(", ")+"</span><br/>"
#   else
#     return ""

# format_postings_for_item = (fqin, postings, nick) ->
#   p2list=("<a href=\"/postable/#{p}/filter/html\">#{p}</a>" for p in postings[fqin] when p isnt "#{nick}/group:default")
#   if p2list.length >0
#     return "<span>Posted in "+p2list.join(", ")+"</span><br/>"
#   else
#     return ""

# format_items = ($sel, nick, items, count, stags, notes, postings, formatter, asform=false) ->
#   adslocation = "http://labs.adsabs.harvard.edu/adsabs/abs/"
#   htmlstring = ""
#   for i in items
#     fqin=i.basic.fqin
#     url=adslocation + "#{i.basic.name}"
#     htmlstring = htmlstring + "<#{formatter}><a href=\"#{url}\">#{i.basic.name}</a><br/>"
#     htmlstring=htmlstring+format_tags_for_item(fqin, stags, nick)
#     htmlstring=htmlstring+format_postings_for_item(fqin, postings, nick)
#     htmlstring=htmlstring+format_notes_for_item(fqin, notes, nick)  
#     htmlstring=htmlstring+"</#{formatter}>"
#     if asform
#       htmlstring=htmlstring+w.postalnote_form()

#     $sel.prepend(htmlstring)
#   $('#breadcrumb').append("#{count} items")
#Model, This should do the Individual notes too

cdict=(fqin, l)->
    d={}
    d[fqin]=l
    return d

class ItemView extends Backbone.View
     
  tagName: 'div'
  className: 'control-group'

  events:
    "click .notebtn" : "submitNote"

  initialize: (options) ->
    {@stags, @notes, @item, @postings, @memberable, @noteform} = options
    console.log "PVIN",  @memberable
    @hv=undefined

  update: (postings, notes, tags) =>
    @stags=tags
    @notes=notes
    @postings=postings

  render: =>
    @$el.empty()
    adslocation = "http://labs.adsabs.harvard.edu/adsabs/abs/"
    url=adslocation + "#{@item.basic.name}"
    htmlstring = "<a href=\"#{url}\">#{@item.basic.name}</a><br/>"
    fqin=@item.basic.fqin
    content = ''
    content = content + htmlstring
    #additional = format_stuff(fqin, @memberable, cdict(fqin,@stags), cdict(fqin,@postings), cdict(fqin,@notes))
    additional = format_tags_for_item(fqin, cdict(fqin,@stags), @memberable)
    additional = additional + format_postings_for_item(fqin, cdict(fqin, @postings), @memberable)
    content = content + additional
    @$el.append(content)
    if @noteform
        @hv= new w.HideableView({state:0, widget:w.postalnote_form("make note",2, 0), theclass: ".postalnote"})
        @$el.append(@hv.render("Notes:").$el)
        if @hv.state is 0
            @hv.hide()
    #w.postalnote_form("make note")
    @$el.append(format_notes_for_item(fqin, cdict(fqin,@notes), @memberable))
    return this

  update_note: (data) =>
    fqin=@item.basic.fqin
    [stags, notes]=get_taggings(data)
    @stags=stags[fqin]
    @notes=notes[fqin]
    @render()

  submitNote: =>
    console.log "IN SUBMIT NOTE"
    item=@item.basic.fqin
    notetext= @$('.txt').val()
    console.log notetext
    loc=window.location
    cback = (data) =>
        console.log "return data", data, loc
        #window.location=loc
        @update_note(data)
    eback = (xhr, etext) =>
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    syncs.submit_note(item, notetext, cback, eback)
    return false

#Collection for change postform
class ItemsView extends Backbone.View

  events:
    "click .post" : "submitPosts"
    "click .tag" : "submitTags"
    "click .done" : "iDone"

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @loc, @noteform} = options
    console.log "ITEMS", @items, @loc

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
                console.log "POSTINGSSSSSSSSSSSSSSSS", @postings[k]
            else
                @postings[k]=[]
        for i in @items
            fqin=i.basic.fqin
            @itemviews[fqin].update(@postings[fqin], @notes[fqin], @stags[fqin])
            @itemviews[fqin].render()


  render: =>
    $lister=@$('.items')
    $lister.append('<legend>Selected Items</legend>')
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
        console.log "INS", ins
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
        console.log "return data", data, @loc
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
    console.log "MAKEPUBLIC", makepublic
    if makepublic
        postables=postables.concat ['adsgut/group:public']
    loc=window.location
    cback = (data) =>
        console.log "return data", data, loc
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
    console.log "TAGSTRING", tagstring
    if tagstring is ""
        console.log "a"
        tags=[]
    else
        console.log "b", (e for e in tagstring.split(','))
        tags=(e.trim() for e in tagstring.split(','))
        tags=(e for e in tags when e != "")
    loc=window.location
    cback = (data) =>
        console.log "return data", data, loc
        #window.location=loc
        @$('.tagsinput').val("")
        @update_postings_taggings()
    eback = (xhr, etext) =>
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    syncs.submit_tags(@items, tags, cback, eback)
    return false

#now create an itemsview for the filter page
class ItemsFilterView extends Backbone.View

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @noteform} = options
    console.log "ITEMS", @items

  render: =>
    console.log "EL", @$el
    for i in @items
        fqin=i.basic.fqin
        ins = 
            stags: @stags[fqin]
            notes: @notes[fqin]
            postings: @postings[fqin]
            item: i
            memberable: @memberable
            noteform: @noteform
        console.log "INS", ins
        v=new ItemView(ins)
        @$el.append(v.render().el)

    return this


root.itemsdo=
    ItemView: ItemView
    ItemsView: ItemsView
    ItemsFilterView: ItemsFilterView