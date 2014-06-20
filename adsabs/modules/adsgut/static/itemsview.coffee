root = exports ? this
$=jQuery
h = teacup
w = widgets
prefix=GlobalVariables.ADS_PREFIX+'/adsgut'

cdict=(fqin, l)->
    d={}
    d[fqin]=l
    return d


parse_fqin = (fqin) ->
    vals=fqin.split(':')
    return vals[-1+vals.length]

#bug we dont have target set for this
enval = (tag) ->
    ename = encodeURIComponent(tag.text)
    if not tag.url
        tag.url = "#{prefix}/postable/#{@memberable.nick}/library:default/filter/html?query=tagname:#{ename}&query=tagtype:ads/tagtype:tag"
        title = tag.title ? ' data-toggle="tooltip" title="' + tag.title + '"' : '';
        #tag.text = '<a class="tag-link" ' + title + ' target="' + tagger.options.tag_link_target + '" href="' + tag.url + '">' + tag.text + '</a>';
        tag.id = tag.text
        tag.pview=@pview
        tag.text = '<a class="tag-link" ' + title +  '" href="' + tag.url + '">' + tag.text + '</a>';
        tag.by = true
        #console.log("taggb",tag);
    return tag

#IMPORTANT:in the individual item case we do the submit, but we dont roundtrip to regen the tags
addwa = (tag, cback) ->
    #tags = [tag.id]
    #items = [@item]
    #console.log items, tag
    eback = (xhr, etext) =>
        #console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    syncs.submit_tag(@item.basic.fqin, @item.basic.name, tag.id, tag.pview, cback, eback)

addwoa = (tag, cback) ->
    #console.log "NEWTAG IN ADDWOA", tag
    @update_tags(tag.id)
    cback()
    #console.log "NEWTAGS", @newtags

remIndiv = (pill) ->
    tag = $(pill).attr('data-tag-id')
    fqtn = $(pill).attr('data-tag-fqtn')
    #console.log "TAGALOG", @pview, @tagajaxsubmit
    if not @tagajaxsubmit
        #console.log "OLDNEWTAGS1", @tagajaxsubmit, @newtags
        @remove_from_tags(tag)
        #console.log "NEWNEWTAGS", @newtags
    else
        eback = (xhr, etext) =>
            alert 'Did not succeed'
        cback = (data) =>

        syncs.remove_tagging(@item.basic.fqin, tag, fqtn, @pview, cback, eback)

time_format_iv = (timestring) ->
    return timestring.split('.')[0].split('T').join(" at ")

didupost = (postings, you, fqpn, areyouowner) ->
    counter=0
    youposted=false
    if areyouowner
        return true
    for p in postings
        if p[0]==fqpn
            counter = counter + 1
        if p[1]==you.adsid
            youposted=true
    #console.log postings, you, fqpn, counter, youposted
    if youposted==true and counter > 1
        return false
    else if youposted==true and counter <= 1
        return true
    else if youposted==false
        return false

class ItemView extends Backbone.View

  tagName: 'div'
  className: 'itemcontainer'

  events:
    "click .notebtn" : "submitNote"
    "click .removenote" : "removeNote"
    "click .removeitem" : "removeItem"

  initialize: (options) ->
    {@submittable, @counter, @stags, @notes, @item, @postings, @memberable, @noteform, @tagajaxsubmit, @suggestions, @pview, @pviewowner} = options
    @tagsfunc = options.tagfunc ? () ->
    #console.log "PVIN",  @memberable, @pview, @pviewowner
    @hv=undefined
    @newtags = []
    @newnotes = []
    @newposts = []
    @therebenotes=false
    if @notes.length > 0
        @therebenotes=true
    #console.log "PVIEW IS", @e,@pview

  update: (postings, notes, tags) =>
    @stags=tags
    @notes=notes
    @postings=postings

  update_tags: (newtag) =>
    #console.log("#{@item.basic.name} >>>",newtag)
    @newtags.push(newtag)
    @submittable.state = true

  remove_from_tags: (newtag) =>
    #console.log "newtag is", newtag
    @newtags = _.without(@newtags, newtag)

  update_posts: (newposts) =>
    @newposts=_.union(@newposts, newposts)
    @submittable.state = true

  update_notes: (newnotetuple) =>
    @newnotes.push(newnotetuple)
    @submittable.state = true

  remove_notes: (newnotetext) =>
    #console.log "NN", newnotetext, @newnotes
    newernotes=[]
    for ele in @newnotes
        if ele[0] != newnotetext
            newernotes.push(ele)
    @newnotes = newernotes
    #console.log "NN2", @newnotes

  render: =>
    #console.log "STAGS", @stags
    @$el.empty()
    adslocation = GlobalVariables.ADS_ABSTRACT_BASE_URL;
    url=adslocation + "#{@item.basic.name}"
    #console.log ">>", @item.basic.name, @pview, didupost(@postings, @memberable, @pview)
    if @pview not in ['udg', 'pub', 'none'] and didupost(@postings, @memberable, @pview, @pviewowner)
        deleter = '<a class="removeitem" style="cursor:pointer;"><span class="i badge badge-important">x</span></a>'
    else
        deleter = ''
    if @item.whenposted
        htmlstring = "<div class='searchresultl'>(#{@counter}). <a href=\"#{url}\">#{@item.basic.name}</a>&nbsp;&nbsp;(saved #{time_format_iv(@item.whenposted)})&nbsp;&nbsp;#{deleter}</div>"
    else
        htmlstring = "<div class='searchresultl'>(#{@counter}). <a href=\"#{url}\">#{@item.basic.name}</a>&nbsp;&nbsp;#{deleter}</div>"

    fqin=@item.basic.fqin
    content = ''
    content = content + htmlstring
    #additional = format_stuff(fqin, @memberable, cdict(fqin,@stags), cdict(fqin,@postings), cdict(fqin,@notes))
    thetags = format_tags_for_item(@pview, fqin, cdict(fqin,@stags), @memberable, @tagajaxsubmit)
    additional = "<span class='tagls'></span><br/>"
    thepostings = format_postings_for_item(fqin, cdict(fqin, (p[0] for p in @postings)), @memberable.nick)
    additionalpostings = "<strong>In Libraries</strong>: <span class='postls'>#{thepostings.join(', ')}</span><br/>"
    additional = additional + additionalpostings
    content = content + additional
    @$el.append(content)
    #console.log "THETAGS", thetags, @memberable
    #console.log @pview, @pviewowner
    if @pviewowner=='none'
        can_delete = false
    else
        can_delete = @pviewowner
    tagdict =
        values: thetags
        can_delete: can_delete
        enhanceValue: _.bind(enval, this)
        addWithAjax: _.bind(addwa, this)
        addWithoutAjax: _.bind(addwoa, this)
        onAfterAdd: @tagsfunc
        ajax_submit: @tagajaxsubmit
        onRemove: _.bind(remIndiv, this)
        suggestions: @suggestions
        templates:
            pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
            add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">add tag</span>&nbsp;',
            input_pill: '<span></span>&nbsp;'
            ok_icon: '<btn class="btn btn-primary">Apply</btn>'
    if @memberable.nick=='anonymouse'
        tagdict.can_add = false
    #console.log "TAGDICT", tagdict
    jslist=[]
    @.$('.tagls').tags(jslist,tagdict)
    @tagsobject = jslist[0]
    #console.log("TAGSOBJECT", @tagsobject)
    #console.log "PVIEW2 IS", @pview, @noteform, @therebenotes
    if @noteform and @memberable.adsid!='anonymouse'
        @hv= new w.HideableView({state:0, widget:w.postalnote_form("make note",2, @pview), theclass: ".postalnote"})
        @$el.append(@hv.render("<strong>Notes</strong>: ").$el)
        if @hv.state is 0
            @hv.hide()
    if @memberable.adsid=='anonymouse' and @therebenotes
        @$el.append("<div class='anony'><span><strong>Notes</strong>:</span></div>")
    if @therebenotes
        if @memberable.adsid=='anonymouse'
            @.$('.anony').append("<p class='notes'></p>")
        else
            @$el.append("<p class='notes'></p>")
        #console.log "NOTES", @notes
        @.$('.notes').append(format_notes_for_item(fqin, cdict(fqin,@notes), @memberable.adsid, @pview, can_delete))
    @$el.append('<hr style="margin-top: 15px; margin-bottom: 10px;"/>')
    return this

  #this might be better implemented with underscore
  addToPostsView: () =>
    fqin=@item.basic.fqin
    poststoshow=(p for p in @newposts when p not in (po[0] for po in @postings))
    thepostings = format_postings_for_item(fqin, cdict(fqin, poststoshow), @memberable.nick)
    already = format_postings_for_item(fqin, cdict(fqin, (p[0] for p in @postings)), @memberable.nick).join(', ')
    #console.log "THEPOSTINGS", thepostings, already
    inbet = ''
    if already != ''
        inbet= ', '

    #console.log('EEKS', thepostings.join(', '))
    @.$('.postls').html(already+inbet+thepostings.join(', '))

  #notes should return their tagmode eventually
  update_note_ajax: (data) =>
    fqin=@item.basic.fqin
    [stags, notes]=get_taggings(data)
    #console.log "NOTES", notes, "DATA", data
    @stags=stags[fqin]
    @notes=notes[fqin]
    if @notes.length > 0
        @therebenotes = true
    @render()

  submitNote: =>
    #console.log "IN SUBMIT NOTE", @pview, @f, @d, @e
    item=@item.basic.fqin
    itemname=@item.basic.name
    notetext= @.$('.txt').val()
    notemode = '1'
    # if @pview is 'udg'
    #   notemode='0'
    # else
    #   if @.$('.cb').is(':checked')
    #       if @pview is 'pub'
    #           #additionally, item must be made public. should public also mean all groups item is in
    #           #as now. YES.
    #           notemode = '0'
    #       else if @pview is 'none'
    #           notemode = '0'
    #       else
    #           notemode = @pview
    if @.$('.cb').is(':checked')
        if @pview is 'pub'
            #additionally, item must be made public. should public also mean all groups item is in
            #as now. YES.
            notemode = '0'
        else if @pview in ['udg','none']
            notemode = '0'
        else
            notemode = @pview
    ctxt = @pview
    #console.log "NOTESPEC",notetext, notemode, ctxt
    loc=window.location
    cback = (data) =>
        #console.log "return data", data, loc
        #window.location=loc
        @update_note_ajax(data)
        format_item(@$('.searchresultl'),@e)
    eback = (xhr, etext) =>
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    if @tagajaxsubmit
        #console.log "in ajax submit"
        syncs.submit_note(item, itemname, [notetext, notemode], ctxt, cback, eback)
    else
        #console.log "NO AJAX IN NOTES", @therebenotes
        @update_notes([notetext, notemode])
        if not @therebenotes
            #console.log "there werent notes before"
            #start = <table class='table-condensed table-striped'>
            #end = </table>
            @$el.append("<p class='notes'></p>")
            @.$(".notes").append("<table class='table-condensed table-striped'></table>")
            @therebenotes=true
        d = new Date()
        notetime=d.toISOString()
        @.$('.notes table').prepend(format_row("randomid", notetext, notemode, notetime, @memberable, @memberable, false, @pview))
        @hv.hide()
        @.$('.txt').val("")
        @submittable.state = true
    return false

  removeNote: (e) =>
    #console.log "IN REMOVE NOTE", @pview
    item=@item.basic.fqin
    itemname=@item.basic.name
    $target =  $(e.currentTarget)
    cback = (data) =>
        #console.log "return data", data
        #window.location=loc
        @update_note_ajax(data)
        format_item(@$('.searchresultl'),@e)
    eback = (xhr, etext) =>
        #console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    if @tagajaxsubmit
        tagname = $target.attr('id')
        fqtn = $target.attr('data-fqtn')
        syncs.remove_note(item, tagname, fqtn, @pview, cback, eback)
    else
        #console.log "NO AJAX IN NOTES", @therebenotes
        notetext = $target.parents("tr").find("td.notetext").text()
        #console.log "NOTETEXT", notetext
        @remove_notes(notetext)
        $target.parents("tr").remove()
    return false

  removeItem: =>
    #console.log "IN REMOVE NOTE", @pview
    item=@item.basic.fqin
    itemname=@item.basic.name
    cback = (data) =>
        #console.log "return data", data, loc
        #window.location=loc
        @remove()
        #BUG:Also need to bubble it upstairs to collection dictionary
        #best reimplement this in proper backbone soon.
        nump = $('#count').text()
        ix = nump.search('papers')
        nump=Number(nump[0...ix]) - 1
        $('#count').text("#{nump} papers. ")
    eback = (xhr, etext) =>
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    if @tagajaxsubmit
        syncs.remove_items_from_postable([item], @pview, cback, eback)
    return false

addwoata = (tag, cback) ->
    #console.log "IN ADVOATA", tag
    @update_tags(tag)
    cback()

remMulti = (pill) ->
    tag = $(pill).attr('data-tag-id')
    #console.log "TAGALOGMULTI", tag, pill
    if not @tagajaxsubmit
        #console.log "MULTIREM1", @tagajaxsubmit, pill
        for i in @items
            fqin=i.basic.fqin
            #@itemviews[fqin].remove_from_tags(tag.id)
            #console.log "YS", @itemviews[fqin].tagsobject
            @itemviews[fqin].tagsobject.removeTag(@itemviews[fqin].$("[data-tag-id='#{tag}']"))
            #console.log "HERE"
    else
        #console.log "MULTIREM2", @tagajaxsubmit

#This needs to be redone to show changes but not actually do them.
#FOR POSTFORM
class ItemsView extends Backbone.View

  events:
    "click .post" : "submitPosts"
    "click .tag" : "submitTags"
    "click .done" : "iDone"
    "click .cancel" : "iCancel"
    "click .libsub" : "subNewLib"

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @loc, @noteform, @suggestions, @pview, @pviewowner} = options
    @newposts=[]
    #console.log "PVIEW", @pview
    @tagajaxsubmit = false
    @submittable =
        state: false

  update_postings_taggings: () =>
    @postings={}
    #console.log("itys", @items)
    itemlist=("items=#{encodeURIComponent(i.basic.fqin)}" for i in @items)
    itemsq=itemlist.join("&")
    $.get prefix+"/items/taggingsandpostings?#{itemsq}", (data)=>
        [@stags, @notes]=get_taggings(data)
        for own k,v of data.postings
            ##console.log "2>>>", k,v[0],v[1]
            if v[0] > 0
                @postings[k]=(e.posting.postfqin for e in v[1])
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
    @submittable.state = true

  update_posts: (postables) =>
    for p in postables
        @newposts=_.union(@newposts, postables)
    for i in @items
        fqin=i.basic.fqin
        @itemviews[fqin].update_posts(@newposts)
        @itemviews[fqin].addToPostsView()
    @submittable.state = true
    #console.log "NEWPOSTS", @newposts

  render: =>
    $lister=@$('.items')
    #$lister.append('<legend>Selected Items</legend>')
    $ctrls=@$('.ctrls')
    @itemviews={}
    counter=1
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
            suggestions: @suggestions
            pview: @pview
            pviewowner: 'none'
            counter: counter
            submittable: @submittable
        v=new ItemView(ins)
        $lister.append(v.render().el)
        $lister.append('<hr style="margin-top: 10px; margin-bottom: 10px;"/>')
        @itemviews[fqin]=v
        counter = counter + 1
    # for v in views
    #     $lister.append(v.render().el)
    eback = (xhr, etext) =>
        #console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    cback = (data) =>
        #console.log data
        libs=_.union(data.libraries, data.groups).sort()
        #console.log "libsa", libs
        $ctrls.append(w.postalall_form(@nameable, @itemtype, libs))
        tagdict =
            enhanceValue: _.bind(enval, this)
            addWithAjax: _.bind(addwa, this)
            addWithoutAjax: _.bind(addwoata, this)
            ajax_submit: false
            onRemove: _.bind(remMulti, this)
            suggestions: @suggestions
            templates:
                pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
                add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">add tag</span>&nbsp;',
                input_pill: '<span></span>&nbsp;'
                ok_icon: '<btn class="btn btn-primary">Apply</btn>'

        jslist=[]
        @.$('#alltags').tags(jslist,tagdict)
        #console.log("MULTILIBRARY", @.$('.multilibrary'))
        #enableFiltering: true,
        @.$('.multilibrary').multiselect({
                        includeSelectAllOption: true,
                        maxHeight: 150
        })
        @globaltagsobject = jslist[0]
    syncs.get_postables_writable(@memberable.nick, cback, eback)
    return this

  subNewLib: =>
    #console?.log "in sublib"
    postable =
        name: @.$('.libtxt').val()
        description: ''
    postabletype = "library"
    @.$('.libtxt').empty()

    eback = (xhr, etext) =>
        alert 'Did not succeed'

    cback2 = (data) =>
            libs=_.union(data.libraries, data.groups)
            librarychoicedict={}
            for c in libs
                librarychoicedict[c]=parse_fqin(c)
                if postable.name==librarychoicedict[c]
                    value = c
            #console.log "libs", libs, data, @.$('.multilibrary')
            @.$('.posthorizontal').empty()
            @.$('.posthorizontal').append(w.postcontrol(libs, librarychoicedict))
            @.$('.multilibrary').multiselect({
                            includeSelectAllOption: true,
                            maxHeight: 150
            })
            if value
                @.$('.multilibrary').multiselect('select', value)

    cback = (data) =>
        #console.log("data", data, @memberable.nick)
        syncs.get_postables_writable(@memberable.nick, cback2, eback)

    syncs.create_postable(postable, postabletype, cback, eback)

  iCancel: =>
    $.fancybox.close()

  #THIS MUST BE FIXED TO
  #(a) only get the new tags and notes
  #(b) we dont want the tags to go everywhere, we want them to only go where the new postings are
  #this may make the posting slower, or we need to support a routing where we only put the tags into
  #the places where the items hasve now been posted. indeed this can be done in the default case by adding
  #a payload of postables
  iDone: =>
    #loc=window.location
    cback = (data) =>
        #console.log "DATAHOO", data
        #window.location=@loc
        $.fancybox.close()

    eback = (xhr, etext) =>
        #console.log "ERROR", etext
        #replace by a div alert from bootstrap
        alert 'Did not succeed'
    #if you dont do things, atleast save items
    postables = @collectPosts()
    #console.log "P", postables
    ts = @collectTags()
    #console.log "T", ts
    ns = @collectNotes()
    #console.log "N", ns
    cback_notes = ()  =>
        #console.log "SAVING NOTES", ns
        syncs.submit_notes(@items, ns, cback, eback)
    cback_tags = () =>
        #console.log "SAVING TAGS", ts
        syncs.submit_tags(@items, ts, postables, cback_notes, eback)
    cback_posts = () =>
        #console.log "SAVING POSTS", postables
        syncs.submit_posts(@items, postables, cback_tags, eback)

    #console.log "SAVING ITEMS"
    syncs.save_items(@items, cback_posts, eback)


    #SHOULD HAVE A TAB CLOSE
    #window.close()
    return false

  #currently unused
  submitPosts: =>
    libs=@$('.multilibrary').val()
    if libs is null
        libs=[]
    postables=_.without(libs,'multiselect-all')
    #makepublic=@$('.makepublic').is(':checked')
    #if makepublic
    #    postables=postables.concat ['adsgut/group:public']
    $('option', @$('.multilibrary')).each (ele) ->
        ##console.log "$this is", $(this), ele
        $(this).removeAttr('selected').prop('selected', false)
    @$('.multilibrary').multiselect('refresh')
    loc=window.location
    cback = (data) =>
        @update_postings_taggings()
    eback = (xhr, etext) =>
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed saving to libraries'
    if @tagajaxsubmit
        syncs.submit_posts(@items, postables, cback, eback)
    else
        #console.log "submit posts non ajax", postables
        @update_posts(postables)
    return false

  collectTags: =>
    tags={}
    for i in @items
        fqin=i.basic.fqin
        iview=@itemviews[fqin]
        ntags=iview.newtags
        #console.log "<<<???", fqin, ntags, i
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
        notes[fqin]=([e[0].trim(),e[1]] for e in ntags when e[0] != "")
    return notes

  collectPosts: =>
    return @newposts

  #currntly unused
  submitTags: =>
    ts={}
    tagstring=@$('.tagsinput').val()
    if tagstring is ""
        #console.log "a"
        tags=[]
    else
        #console.log "b", (e for e in tagstring.split(','))
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
        #console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert 'Did not succeed tagging'
    syncs.submit_tags(@items, ts, cback, eback)
    return false

#now create an itemsview for the filter page
class ItemsFilterView extends Backbone.View

  initialize: (options) ->
    {@stags, @notes, @$el, @postings, @memberable, @items, @nameable, @itemtype, @noteform, @suggestions, @pview, @pviewowner, @tagfunc} = options
    #console.log "PVIEW", @pview, @postings
    #console.log "ITEMS", @items, @suggestions
    @submittable =
        state: true

  render: =>
    #console.log "EL", @$el
    @itemviews = {}
    counter = 1
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
            suggestions: @suggestions
            pview: @pview
            pviewowner: @pviewowner
            tagfunc: @tagfunc
            counter: counter
            submittable: @submittable
        #console.log "INS", ins, @pview
        v=new ItemView(ins)
        @$el.append(v.render().el)
        @itemviews[fqin] = v
        #@$el.append('<hr style="margin-top: 15px; margin-bottom: 10px;"/>')
        counter = counter + 1
    return this


root.itemsdo=
    ItemView: ItemView
    ItemsView: ItemsView
    ItemsFilterView: ItemsFilterView
