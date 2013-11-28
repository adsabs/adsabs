root = exports ? this
$=jQuery
h = teacup
w = widgets
prefix=GlobalVariables.ADS_PREFIX+'/adsgut'

cdict=(fqin, l)->
    d={}
    d[fqin]=l
    return d

#bug we dont have target set for this
enval = (tag) ->
    ename = encodeURIComponent(tag.text)
    if not tag.url
        tag.url = "#{prefix}/postable/#{@memberable}/group:default/filter/html?query=tagname:#{ename}&query=tagtype:ads/tagtype:tag"
        title = tag.title ? ' data-toggle="tooltip" title="' + tag.title + '"' : '';
        #tag.text = '<a class="tag-link" ' + title + ' target="' + tagger.options.tag_link_target + '" href="' + tag.url + '">' + tag.text + '</a>';
        tag.id = tag.text
        tag.text = '<a class="tag-link" ' + title +  '" href="' + tag.url + '">' + tag.text + '</a>';

        console.log("taggb",tag);
    return tag

addwa = (tag, cback) ->
    tags = [tag.id]
    items = [@item]
    console.log items, tags
    eback = (xhr, etext) =>
        console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    syncs.submit_tags(items, tags, cback, eback)

addwoa = (tag, cback) ->
    console.log "NEWTAG", tag
    @update_tags(tag.id)
    cback()
    console.log "NEWTAGS", @newtags

class ItemView extends Backbone.View
     
  tagName: 'div'
  className: 'itemcontainer'

  events:
    "click .notebtn" : "submitNote"

  initialize: (options) ->
    {@stags, @notes, @item, @postings, @memberable, @noteform, @tagajaxsubmit} = options
    console.log "PVIN",  @memberable
    @hv=undefined
    @newtags = []
    @newnotes = []
    @newposts = []

  update: (postings, notes, tags) =>
    @stags=tags
    @notes=notes
    @postings=postings

  update_tags: (newtag) =>
    console.log(">>>",newtag)
    @newtags.push(newtag)

  update_posts: (newpost) =>
    @newposts.push(newpost)

  update_notes: (newnote) =>
    @newnotes.push(newnote)

  render: =>
    @$el.empty()
    adslocation = "http://labs.adsabs.harvard.edu/adsabs/abs/"
    url=adslocation + "#{@item.basic.name}"
    htmlstring = "<span class='itemtitle'><a href=\"#{url}\">#{@item.basic.name}</a></span><br/>"
    fqin=@item.basic.fqin
    content = ''
    content = content + htmlstring
    #additional = format_stuff(fqin, @memberable, cdict(fqin,@stags), cdict(fqin,@postings), cdict(fqin,@notes))
    thetags = format_tags_for_item(fqin, cdict(fqin,@stags), @memberable)
    additional = "<span class='tagls'></span><br/>"
    thepostings = format_postings_for_item(fqin, cdict(fqin, @postings), @memberable)
    additionalpostings = "<span class='postls'><strong>In Libraries</strong>: #{thepostings.join(', ')}</span><br/>"
    additional = additional + additionalpostings
    content = content + additional
    @$el.append(content)

    tagdict = 
        values: thetags
        enhanceValue: _.bind(enval, this)
        addWithAjax: _.bind(addwa, this)
        addWithoutAjax: _.bind(addwoa, this)
        ajax_submit: @tagajaxsubmit
        templates:
            pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
            add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">new tag</span>&nbsp;',
            input_pill: '<span></span>&nbsp;'
    jslist=[]
    @.$('.tagls').tags(jslist,tagdict)
    @tagsobject = jslist[0]
    console.log("TAGSOBJECT", @tagsobject)
    if @noteform
        @hv= new w.HideableView({state:0, widget:w.postalnote_form("make note",2, 0), theclass: ".postalnote"})
        @$el.append(@hv.render("Notes: ").$el)
        if @hv.state is 0
            @hv.hide()
    #w.postalnote_form("make note")
    @$el.append(format_notes_for_item(fqin, cdict(fqin,@notes), @memberable))
    return this

  update_note_ajax: (data) =>
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
        @update_note_ajax(data)
    eback = (xhr, etext) =>
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    syncs.submit_note(item, notetext, cback, eback)
    return false

#Collection for change postform
addwoata = (tag, cback) ->
    console.log "IN ADVOATA", tag
    @update_tags(tag)
    cback()
#This needs to be redone to show changes but not actually do them.
class ItemsView extends Backbone.View

  events:
    "click .post" : "submitPosts"
    "click .tag" : "submitTags"
    "click .done" : "iDone"

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @loc, @noteform} = options

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

  update_tags: (newtag) =>
    for i in @items
        fqin=i.basic.fqin
        @itemviews[fqin].update_tags(newtag.id)
        @itemviews[fqin].tagsobject.addTag(@itemviews[fqin].$('.pills-list'), newtag)

  render: =>
    $lister=@$('.items')
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
            tagajaxsubmit: false
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
        tagdict = 
            enhanceValue: _.bind(enval, this)
            addWithAjax: _.bind(addwa, this)
            addWithoutAjax: _.bind(addwoata, this)
            ajax_submit: false
            templates:
                pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
                add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">new tag</span>&nbsp;',
                input_pill: '<span></span>&nbsp;'
        jslist=[]
        @.$('#alltags').tags(jslist,tagdict)
        @globaltagsobject = jslist[0]
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

#now create an itemsview for the filter page
class ItemsFilterView extends Backbone.View

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @noteform} = options
    console.log "ITEMS", @items

  render: =>
    console.log "EL", @$el
    #@$el.append('<hr/>')
    for i in @items
        fqin=i.basic.fqin
        ins = 
            stags: @stags[fqin]
            notes: @notes[fqin]
            postings: @postings[fqin]
            item: i
            memberable: @memberable
            noteform: @noteform
            tagajaxsubmit: true
        console.log "INS", ins
        v=new ItemView(ins)
        @$el.append(v.render().el)
        @$el.append('<hr/>')
    return this


root.itemsdo=
    ItemView: ItemView
    ItemsView: ItemsView
    ItemsFilterView: ItemsFilterView