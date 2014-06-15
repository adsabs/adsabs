root = exports ? this
$=jQuery
#console.log "In Funcs"
h = teacup

editable_text =  (text) ->
    return h.render ->
        h.span ".edsp", ->
            h.span ".edtext", text
            h.a ".edclick", href:'#', ->
                h.i ".icon-pencil", style:"padding-left: 5px;"


parse_fqin = (fqin) ->
    vals=fqin.split(':')
    return vals[-1+vals.length]

inline_list = h.renderable (items) ->
    h.ul '.inline',  ->
        for i in items
            h.li i

regular_list = h.renderable (items) ->
    h.ul '.regular',  ->
        for i in items
            h.li i

table_from_dict_partial = h.renderable (k,v) ->
    h.td ->
        h.raw k
    h.td ->
        h.raw v

table_from_dict = h.renderable (kcol, vcol, dict) ->
    h.table '.table.table-bordered.table-condensed.table-striped',  ->
        h.thead ->
            h.tr ->
                h.th ".#{kcol.replace(/\s+/g, '')}", kcol
                h.th ".#{vcol.replace(/\s+/g, '')}", vcol
        h.tbody ->
            for k,v of dict
                h.tr ->
                    table_from_dict_partial(k,v)

$table_from_dict = (kcol, vcol, vlist) ->
    f=h.renderable (kcol, vcol) ->
        h.table '.table.table-bordered.table-condensed.table-striped',  ->
            h.thead ->
                h.tr ->
                    h.th ".#{kcol.replace(/\s+/g, '')}", kcol
                    h.th ".#{vcol.replace(/\s+/g, '')}", vcol
            h.tbody
    $f=$(f(kcol,vcol))
    for k in vlist
        $f.append(k)
    return $f

table_from_dict_partial_many = h.renderable (k,vlist) ->
    h.td ->
        h.raw k
    for ele in vlist
        h.td ->
            h.raw ele

table_from_dict_many = h.renderable (kcol, vcollist, dict) ->
    h.table '.table.table-bordered.table-condensed.table-striped',  ->
        h.thead ->
            h.tr ->
                h.th ".#{kcol.replace(/\s+/g, '')}", kcol
                for ele in vcollist
                    h.th ".#{ele.replace(/\s+/g, '')}", ele
        h.tbody ->
            for k,vlist of dict
                h.tr ->
                    table_from_dict_partial_many(k,vlist)

$table_from_dict_many = (kcol, vcollist, vlist) ->
    f=h.renderable (kcol, vcollist) ->
        h.table '.table.table-bordered.table-condensed.table-striped',  ->
            h.thead ->
                h.tr ->
                    h.th ".#{kcol.replace(/\s+/g, '')}", kcol
                    for ele in vcollist
                        h.th ".#{ele.replace(/\s+/g, '')}", ele
            h.tbody
    $f=$(f(kcol,vcollist))
    for k in vlist
        $f.append(k)
    return $f

one_col_table_partial = h.renderable (k) ->
    h.td ->
        h.raw k

one_col_table = h.renderable (kcol, tlist) ->
    h.table '.table.table-bordered.table-condensed.table-striped',  ->
        h.thead ->
            h.tr ->
                h.th ".#{kcol.replace(/\s+/g, '')}", kcol
        h.tbody ->
            for k in tlist
                h.tr ->
                    one_col_table_partial k

$one_col_table = (kcol, vlist) ->
    f=h.renderable (kcol) ->
        h.table '.table.table-bordered.table-condensed.table-striped',  ->
            h.thead ->
                h.tr ->
                    h.th ".#{kcol.replace(/\s+/g, '')}", kcol
            h.tbody
    $f=$(f(kcol))
    for k in vlist
        $f.append(k)
    return $f


# <div class="input-append">
#   <input class="span2" id="appendedInputButton" type="text">
#   <button class="btn" type="button">Go!</button>
# </div>
#one_submit needs to have an event handler added
one_submit = h.renderable (ltext, btext) ->
    h.label ltext
    h.form ".form-inline", ->
        h.input ".span3.txt", type: 'text'
        h.raw "&nbsp;&nbsp;&nbsp;"
        h.button ".btn.btn-primary.sub", type: 'button', btext

zero_submit = h.renderable (ltext, btext) ->
    h.label ltext
    h.form ".form-inline", ->
        h.raw "&nbsp;&nbsp;&nbsp;"
        h.button ".btn.btn-primary.sub", type: 'button', btext

two_submit = h.renderable (ltext1, ltext2, btext) ->
    h.form ".form-horizontal", ->
        h.div ".control-group", ->
            h.label ".control-label",  ltext1
            h.div ".controls", ->
                h.input ".span4.txt1", type: 'text'
        h.div ".control-group", ->
            h.label ".control-label", ltext2
            h.div ".controls", ->
                h.textarea ".span4.txt2", rows:2
                h.raw "&nbsp;&nbsp;&nbsp;"
                h.button ".btn.btn-primary.sub", type: 'button', btext

one_submit_with_cb = h.renderable (ltext, btext, ctext) ->
    h.label ltext
    h.form ".form-inline", ->
        h.input ".span3.txt", type: 'text'
        h.raw "&nbsp;&nbsp;"
        h.label '.checkbox', ->
            h.input ".cb", type: 'checkbox'
            h.text ctext
        h.raw "&nbsp;&nbsp;&nbsp;"
        h.button ".btn.btn-primary.sub", type: 'button', btext

dropdown_submit = h.renderable (selects, selectnames, ltext, btext) ->
    h.label ltext
    h.form '##{wname}.form-inline', ->
        h.select ".sel", ->
            for s in selects
                h.option value:s, selectnames[s]
        h.raw "&nbsp;&nbsp;&nbsp;"
        h.button ".btn.btn-primary.sub", type: 'button', btext

dropdown_submit_with_cb = h.renderable (selects, selectnames, ltext, btext, ctext) ->
    h.label ltext
    h.form '.form-inline', ->
        h.select ".sel", ->
            for s in selects
                h.option value:s, selectnames[s]
        h.raw "&nbsp;&nbsp;"
        h.label '.checkbox', ->
            h.input ".cb", type: 'checkbox'
            h.text ctext
        h.raw "&nbsp;&nbsp;&nbsp;"
        h.button ".btn.btn-primary.sub", type: 'button', btext

info_layout = h.renderable (dict, keysdict) ->
  h.dl '.dl-horizontal', ->
    for k of keysdict
        h.dt keysdict[k]
        h.dd ->
            h.raw dict[k]

#<button class="btn btn-small" type="button">Small button</button>
single_button = h.renderable (btext) ->
    h.button '.btn.btn-mini.btn-primary.yesbtn', type:'button', btext

single_button_label = h.renderable (ltext, btext) ->
    h.text ltext
    h.raw "&nbsp;&nbsp;"
    h.button '.btn.btn-mini.btn-primary.yesbtn', type:'button', btext

# <div class=\"control-group\">
#   <label class=\"control-label\">Add Note</label>
#   <input type=\"text\" class=\"controls input-xxlarge\" placeholder=\"Type a note…\">
#   <label class=\"checkbox control-label\">
#     <input type=\"checkbox\" class=\"controls\"> Make Private
#   </label>
# </div>
#postalnote_form = h.renderable (htmlstring, additional, btext, nrows=2) ->

class HideableView extends Backbone.View
    tagName: 'div'
    className: 'hideable'

    events:
        "click .hider" : "toggle"

    initialize: (options) ->
        {@widget, @state, @theclass} = options

    toggle: () =>
        #console.log "in toggle", @state
        if @state is 0
            @show()
        else
            @hide()
        return false

    hide: () =>
        #console.log "HIDE"
        @$('.hider .i').html('+')
        @state = 0
        @$(@theclass).hide()

    show: () =>
        @state=1
        @$(@theclass).show()
        #@$('.hider i').attr("class", "icon-minus")
        @$('.hider .i').html('-&nbsp;')

    render: (htext) =>
        content = h.render ->
            h.span ->
                h.raw htext
                h.raw "&nbsp;"
                #h.a ".btn.btn-link.hider", href:'#', ->
                    #h.i ".icon-plus"
                h.a ".hider", href='#', ->
                    h.span '.i.label.label-info', '+'
        @$el.append(content+@widget)
        return this

#widget most be a div widget implementing the hoverhelp class
#using delegation, hovering anywhere inside that div will pop up a help text
$.fn.andFind = (expr) ->
  return this.find(expr).add(this.filter(expr))

class HoverHelpDecoratorView extends Backbone.View

    initialize: (options) ->
        {@titletext, @helptext, @position, @htype, @trigtype} = options

    render: () =>
        optpo=
            placement: @position
            trigger: @trigtype
            container: 'body'
        if @htype is "tooltip"
            optpo.title = @helptext
            @$el.andFind('.hoverhelp').tooltip(optpo)
        else if @htype is "popover"
            optpo.title = @titletext
            optpo.content = @helptext
            @$el.andFind('.hoverhelp').popover(optpo)
        return this

decohelp  = (el, helptext, htype, position, trigtype="hover") ->
    #console.log "EL: ", el, $(el)
    if trigtype == 'click'
        $(el).append('&nbsp;[<a href="#" class="hoverhelp" onclick="return false;">?</a>]')
    else if trigtype == 'hover'
        $(el).append('&nbsp;<i class="hoverhelp icon-question-sign"></i>')
    opt =
        titletext: ""
        helptext: helptext
        position: position
        htype: htype
        el: el
        trigtype : trigtype
    return new HoverHelpDecoratorView(opt).render()

postalnote_form = h.renderable (btext, nrows=2, pview) ->
    #h.div ".control-group.postalnote", ->
    #h.raw htmlstring
    #h.br()
    #h.raw additional
    #<a class="btn" href="#"><i class="icon-align-justify"></i></a>
    #console.log "PVIEW3 IS", pview
    if pview in ['udg','none']
        notetext = 'Make note visible to members of all libraries this item is in (notes are private by default)'
    else if pview is 'pub'
        notetext = 'Make note visible to members of the public (notes are private by default)'
    else
        notetext = 'Make note visible to members of this library (notes are private by default)'
    h.div ".postalnote", ->
        h.textarea ".controls.input-xlarge.txt", type:"text", rows:'#{nrows}', placeholder:"Type a note"
        # if pview != 'udg'
        #   h.label ".control-label", ->
        #       h.input ".control.cb", type:'checkbox'
        #       h.text notetext
        #       h.raw "&nbsp;&nbsp;"
        # else
        #   h.label ".control-label", ""
        h.label ".control-label", ->
            h.input ".control.cb", type:'checkbox'
            h.text notetext
            h.raw "&nbsp;&nbsp;"
        h.button '.btn.btn-primary.btn-mini.notebtn', type:'button', btext

#     <legend>Tagging and Posting</legend>
#     {% if nameable %}
#       <div class="control-group">
#         <label class="control-label">Name this {{itemtype}}</label>
#         <input class="controls" type="text" placeholder="Name for {{itemtype}}…">
#       </div>
#     {% endif %}
#     <div class="control-group">
#       <label class="checkbox control-label">
#         <input class="controls" type="checkbox"> Make Public
#       </label>
#     </div>
#     <div class="control-group">
#       <label id="libslabel" class="control-label">Libraries</label>
#       <input class="controls" type="text" placeholder="Library Name…">
#     </div>
#     <div class="control-group">
#       <label id="groupslabel" class="control-label">Groups</label>
#       <input class="controls" type="text" placeholder="Group Name…">
#     </div>
#     <div class="control-group">
#       <label class="control-label">Tags</label>
#       <input class="controls" type="text" placeholder="Tag Name…">
#     </div>
#     <button type="submit" class="btn">Submit</button>

multiselect = h.renderable (daclass, choices, choicedict) ->
    #console.log "IN MULTISELECT"
    h.select ".multi#{daclass}", multiple:"multiple", ->
        #h.option value:'new', "Create New Library"
        for c in choices
            h.option  value: c, choicedict[c]

addchoices = h.renderable (choices, choicedict) ->
    h.raw ->
        for c in choices
            h.option  value: c, choicedict[c]

#this should not be here. it should be built up hierarchically from other widgets and should itself be in views.
postcontrol = h.renderable (librarychoices, librarychoicedict) ->
    h.div ".control-group.postcontrol", ->
        h.input ".span2.libtxt", type: 'text'
        h.raw "&nbsp;&nbsp;"
        h.button ".btn.btn-primary.libsub", type: 'button', "Create New"
        h.raw "<p></p>"
        multiselect("library", librarychoices, librarychoicedict)
        h.raw "&nbsp;&nbsp;"
        h.button ".btn.btn-primary.post", type:'button', "Apply"


postalall_form = h.renderable (nameable, itemtype, librarychoices) ->
    #console.log "librarych"
    librarychoicedict={}
    for c in librarychoices
        librarychoicedict[c]=parse_fqin(c)
    #console.log "WEE", librarychoicedict

    h.legend "Save all of these items"
    if nameable
        h.div ".control-group", ->
            h.label ".control-label", "Name this #{itemtype}"
            h.input ".controls", type:text, placeholder:"Name for #{itemtype}"
    # h.div ".control-group", ->
    #     h.label ".checkbox.control-label", ->
    #         h.input ".controls.makepublic", type:"checkbox"
    #         h.text "Post to Public feed"

    h.label  "Libraries"
    h.div ".form-horizontal.posthorizontal", ->
        postcontrol(librarychoices, librarychoicedict)
    h.br()
    h.br()
    h.legend "Tag all of these items"
    h.p "Note: Tags will be automatically visible in the groups these items are posted to! Tags may not contain commas."
    #h.div ".control-group", ->
        #h.label ".control-label", "Tags"
    #h.input ".controls.tagsinput.input-xxlarge", type:"text", placeholder:"tags, comma separated"
    #h.button ".btn.btn-primary.tag", type:'button', "Tag"
    h.span "#alltags.tagls"
    h.br()
    h.button ".btn.btn-inverse.done.pull-right.savebutton", type:'button', "Save"
    h.button ".btn.btn-inverse.cancel.pull-right", type:'button', style:"margin-right: 10px;", "Cancel"


link = h.renderable (url, txt) ->
    h.raw "<a href=\"#{url}\">#{txt}</a>"

root.widgets =
    postalall_form: postalall_form
    postalnote_form: postalnote_form
    single_button: single_button
    single_button_label: single_button_label
    inline_list: inline_list
    regular_list: regular_list
    info_layout: info_layout
    one_col_table_partial: one_col_table_partial
    one_col_table: one_col_table
    $one_col_table: $one_col_table
    table_from_dict_partial: table_from_dict_partial
    table_from_dict: table_from_dict
    $table_from_dict: $table_from_dict
    table_from_dict_partial_many: table_from_dict_partial_many
    table_from_dict_many: table_from_dict_many
    $table_from_dict_many: $table_from_dict_many
    one_submit: one_submit
    zero_submit: zero_submit
    dropdown_submit: dropdown_submit
    one_submit_with_cb: one_submit_with_cb
    dropdown_submit_with_cb: dropdown_submit_with_cb
    link: link
    HideableView: HideableView
    HoverHelpDecoratorView: HoverHelpDecoratorView
    decohelp: decohelp
    two_submit: two_submit
    editable_text: editable_text
    postcontrol: postcontrol
