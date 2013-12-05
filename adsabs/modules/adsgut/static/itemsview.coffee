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

#IMPORTANT:in the individual item case we do the submit, but we dont roundtrip to regen the tags
addwa = (tag, cback) ->
    #tags = [tag.id]
    #items = [@item]
    console.log items, tag
    eback = (xhr, etext) =>
        console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    syncs.submit_tag(@item.basic.fqin, @item.basic.name, tag.id, cback, eback)

addwoa = (tag, cback) ->
    console.log "NEWTAG IN ADDWOA", tag
    @update_tags(tag.id)
    cback()
    console.log "NEWTAGS", @newtags

remIndiv = (pill) ->
    tag = $(pill).attr('data-tag-id')
    console.log "TAGALOG", tag, pill
    if not @tagajaxsubmit
        console.log "OLDNEWTAGS1", @tagajaxsubmit, @newtags
        @remove_from_tags(tag)
        console.log "NEWNEWTAGS", @newtags
    else
        console.log "INDIVREM2", @tagajaxsubmit

class ItemView extends Backbone.View
     
  tagName: 'div'
  className: 'itemcontainer'

  events:
    "click .notebtn" : "submitNote"

  initialize: (options) ->
    {@stags, @notes, @item, @postings, @memberable, @noteform, @tagajaxsubmit} = options
    console.log "PVIN",  @memberable, @postings
    @hv=undefined
    @newtags = []
    @newnotes = []
    @newposts = []
    @therebenotes=false
    if @notes.length > 0
        @therebenotes=true

  update: (postings, notes, tags) =>
    @stags=tags
    @notes=notes
    @postings=postings

  update_tags: (newtag) =>
    console.log("#{@item.basic.name} >>>",newtag)
    @newtags.push(newtag)

  remove_from_tags: (newtag) =>
    console.log "newtag is", newtag
    @newtags = _.without(@newtags, newtag)

  update_posts: (newposts) =>
    @newposts=_.union(@newposts, newposts)

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
    additionalpostings = "<strong>In Libraries</strong>: <span class='postls'>#{thepostings.join(', ')}</span><br/>"
    additional = additional + additionalpostings
    content = content + additional
    @$el.append(content)

    tagdict = 
        values: thetags
        enhanceValue: _.bind(enval, this)
        addWithAjax: _.bind(addwa, this)
        addWithoutAjax: _.bind(addwoa, this)
        ajax_submit: @tagajaxsubmit
        onRemove: _.bind(remIndiv, this)
        templates:
            pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
            add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">add tag</span>&nbsp;',
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
        if @therebenotes
            @$el.append("<p class='notes'></p>")
            @.$('.notes').append(format_notes_for_item(fqin, cdict(fqin,@notes), @memberable))
    return this

  #this might be better implemented with underscore
  addToPostsView: () =>
    fqin=@item.basic.fqin
    poststoshow=(p for p in @newposts when p not in @postings)
    thepostings = format_postings_for_item(fqin, cdict(fqin, poststoshow), @memberable)
    already = format_postings_for_item(fqin, cdict(fqin, @postings), @memberable).join(', ')
    console.log "THEPOSTINGS", thepostings, already
    inbet = ''
    if already != ''
        inbet= ', '

    console.log('EEKS', thepostings.join(', '))
    @.$('.postls').html(already+inbet+thepostings.join(', '))

  update_note_ajax: (data) =>
    fqin=@item.basic.fqin
    [stags, notes]=get_taggings(data)
    @stags=stags[fqin]
    @notes=notes[fqin]
    @therebenotes = true
    @render()

  submitNote: =>
    console.log "IN SUBMIT NOTE"
    item=@item.basic.fqin
    itemname=@item.basic.name
    notetext= @.$('.txt').val()
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
    if @tagajaxsubmit
        console.log "in ajax submit"
        syncs.submit_note(item, itemname, notetext, cback, eback)
    else
        console.log "NO AJAX IN NOTES"
        @update_notes(notetext)
        if not @therebenotes
            console.log "there werent notes before"
            @$el.append("<p class='notes'></p>")
            @therebenotes=true
        @.$('.notes').prepend("<span>#{notetext}</span><br/>")
        @hv.hide()
        @.$('.txt').val("")
    return false



addwoata = (tag, cback) ->
    console.log "IN ADVOATA", tag
    @update_tags(tag)
    cback()

remMulti = (pill) ->
    tag = $(pill).attr('data-tag-id')
    console.log "TAGALOGMULTI", tag, pill
    if not @tagajaxsubmit
        console.log "MULTIREM1", @tagajaxsubmit, pill
        for i in @items
            fqin=i.basic.fqin
            #@itemviews[fqin].remove_from_tags(tag.id)
            console.log "YS", @itemviews[fqin].tagsobject
            @itemviews[fqin].tagsobject.removeTag(@itemviews[fqin].$("[data-tag-id='#{tag}']"))
            console.log "HERE"
    else
        console.log "MULTIREM2", @tagajaxsubmit

#This needs to be redone to show changes but not actually do them.
#FOR POSTFORM
class ItemsView extends Backbone.View

  events:
    "click .post" : "submitPosts"
    "click .tag" : "submitTags"
    "click .done" : "iDone"

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @loc, @noteform} = options
    @newposts=[]
    @tagajaxsubmit = false

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
        #below is not needed, it gets autocalled?
        #@itemviews[fqin].update_tags(newtag.id)
        @itemviews[fqin].tagsobject.addTag(@itemviews[fqin].$('.pills-list'), newtag)

  update_posts: (postables) =>
    for p in postables
        @newposts=_.union(@newposts, postables)
    for i in @items
        fqin=i.basic.fqin
        @itemviews[fqin].update_posts(@newposts)
        @itemviews[fqin].addToPostsView()
    console.log "NEWPOSTS", @newposts

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
            tagajaxsubmit: @tagajaxsubmit
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
            onRemove: _.bind(remMulti, this)
            templates:
                pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
                add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">add tag</span>&nbsp;',
                input_pill: '<span></span>&nbsp;'
        jslist=[]
        @.$('#alltags').tags(jslist,tagdict)
        console.log("MULTILIBRARY", @.$('.multilibrary'))
        @.$('.multilibrary').multiselect({
                        includeSelectAllOption: true,
                        enableFiltering: true,
                        maxHeight: 150
        })
        @globaltagsobject = jslist[0]
    syncs.get_postables_writable(@memberable, cback, eback)
    return this

  iDone: =>
    #loc=window.location
    cback = (data) =>
        console.log "DATAHOO", data
        window.location=@loc
        #window.close()
        
    eback = (xhr, etext) =>
        console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    #if you dont do things, atleast save items
    postables = @collectPosts()
    console.log "P", postables
    ts = @collectTags()
    console.log "T", ts
    ns = @collectNotes()
    console.log "N", ns
    cback_notes = ()  =>
        console.log "SAVING NOTES", ns
        syncs.submit_notes(@items, ns, cback, eback)
    cback_tags = () =>
        console.log "SAVING TAGS", ts
        syncs.submit_tags(@items, ts, cback_notes, eback)
    cback_posts = () =>
        console.log "SAVING POSTS", postables
        syncs.submit_posts(@items, postables, cback_tags, eback)
    
    console.log "SAVING ITEMS"
    syncs.save_items(@items, cback_posts, eback)
    
    
    #SHOULD HAVE A TAB CLOSE
    #window.close()
    return false

  submitPosts: =>
    libs=@$('.multilibrary').val()
    if libs is null
        libs=[]
    postables=_.without(libs,'multiselect-all')
    #makepublic=@$('.makepublic').is(':checked')
    #if makepublic
    #    postables=postables.concat ['adsgut/group:public']
    $('option', @$('.multilibrary')).each (ele) ->
        #console.log "$this is", $(this), ele
        $(this).removeAttr('selected').prop('selected', false)
    @$('.multilibrary').multiselect('refresh')
    loc=window.location
    cback = (data) =>
        #window.location=loc
        @update_postings_taggings()
    eback = (xhr, etext) =>
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed saving to libraries'
    if @tagajaxsubmit
        syncs.submit_posts(@items, postables, cback, eback)
    else
        console.log "submit posts non ajax", postables
        @update_posts(postables)
    return false

  collectTags: =>
    tags={}
    for i in @items
        fqin=i.basic.fqin
        iview=@itemviews[fqin]
        ntags=iview.newtags
        console.log "<<<???", fqin, ntags, i
        tags[fqin]=(e.trim() for e in ntags when e != "")
    return tags

  collectNotes: =>
    notes={}
    for i in @items
        fqin=i.basic.fqin
        iview=@itemviews[fqin]
        if iview.therebenotes
            ntags = iview.newnotes
        else
            ntags=[]
        notes[fqin]=(e.trim() for e in ntags when e != "")
    return notes

  collectPosts: =>
    return @newposts

  submitTags: =>
    ts={}
    tagstring=@$('.tagsinput').val()
    if tagstring is ""
        console.log "a"
        tags=[]
    else
        console.log "b", (e for e in tagstring.split(','))
        tags=(e.trim() for e in tagstring.split(','))
        tags=(e for e in tags when e != "")
    loc=window.location
    for i in @items
        fqin=i.basic.fqin
        ts[fqin]=tags
    cback = (data) =>
        #window.location=loc
        #@$('.tagsinput').val("")
        @update_postings_taggings()
    eback = (xhr, etext) =>
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed tagging'
    syncs.submit_tags(@items, ts, cback, eback)
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