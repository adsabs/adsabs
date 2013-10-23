root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup

inline_list = h.renderable (items) ->
    h.ul '.inline',  ->
        for i in items
            h.li i

regular_list = h.renderable (items) ->
    h.ul '.regular',  ->
        for i in items
            h.li i

table_from_dict_partial = h.renderable (k,v) ->
    h.td k
    h.td ->
        h.raw v

table_from_dict = h.renderable (kcol, vcol, dict) ->
    h.table '.table.table-bordered.table-condensed.table-striped',  ->
        h.thead ->
            h.tr ->
                h.th kcol
                h.th vcol
        h.tbody ->
            for k,v of dict
                h.tr ->
                    table_from_dict_partial(k,v)

$table_from_dict = (kcol, vcol, vlist) ->
    f=h.renderable (kcol, vcol) ->
        h.table '.table.table-bordered.table-condensed.table-striped',  ->
            h.thead ->
                h.tr ->
                    h.th kcol
                    h.th vcol
            h.tbody
    $f=$(f(kcol,vcol))
    for k in vlist
        $f.append(k)
    return $f


one_col_table_partial = h.renderable (k) ->
    console.log "HTMLOUT",k,h.html
    h.td ->
        h.raw k

one_col_table = h.renderable (kcol, tlist) ->
    h.table '.table.table-bordered.table-condensed',  ->
        h.thead ->
            h.tr ->
                h.th kcol
        h.tbody ->
            for k in tlist
                h.tr ->
                    one_col_table_partial k

$one_col_table = (kcol, vlist) ->
    f=h.renderable (kcol) ->
        h.table '.table.table-bordered.table-condensed',  ->
            h.thead ->
                h.tr ->
                    h.th kcol
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

dropdown_submit = h.renderable (selects, ltext, btext) ->
    h.label ltext
    h.form '##{wname}.form-inline', ->
        h.select ".sel", ->
            for s in selects
                h.option s
        h.raw "&nbsp;&nbsp;&nbsp;"
        h.button ".btn.btn-primary.sub", type: 'button', btext

dropdown_submit_with_cb = h.renderable (selects, ltext, btext, ctext) ->
    h.label ltext
    h.form '.form-inline', ->
        h.select ".sel", ->
            for s in selects
                h.option s
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
        h.dd dict[k]

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
postalnote_form = h.renderable (btext, nrows=2) ->
    #h.div ".control-group.postalnote", ->
    #h.raw htmlstring
    #h.br()
    #h.raw additional
    h.textarea ".controls.input-xlarge.txt", type:"text", rows:'#{nrows}', placeholder:"Type a note"
    h.label ".control-label", ->
        h.input ".control.cb", type:'checkbox'
        h.text "note private?"
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

multiselect = h.renderable (daclass, choices) -> 
    h.select ".multi#{daclass}", multiple:"multiple", ->
        for c in choices
            h.option c

#this should not be here. it should be built up hierarchically from other widgets and should itself be in views.
postalall_form = h.renderable (nameable, itemtype, groupchoices, librarychoices) ->
    h.legend "Post ALL"
    if nameable
        h.div ".control-group", ->
            h.label ".control-label", "Name this #{itemtype}"
            h.input ".controls", type:text, placeholder:"Name for #{itemtype}"
    h.div ".control-group", ->
        h.label ".checkbox.control-label", ->
            h.input ".controls.makepublic", type:"checkbox"
            h.text "Make Public"
    h.div ".control-group", ->
        h.label ".control-label", "Libraries"
        #h.input ".controls.librariesinput.input-xxlarge", type:"text", placeholder:"Lib names, comma separated" 
        multiselect("library", librarychoices)
    h.div ".control-group", ->
        h.label ".control-label", "Groups"
        #h.input ".controls.groupsinput.input-xxlarge", type:"text", placeholder:"Grp names, comma separated"
        multiselect("group",groupchoices)
    h.button ".btn.btn-primary.post", type:'button', "Post"
    h.br()
    h.br()
    h.legend "Tag ALL"
    #h.div ".control-group", ->
        #h.label ".control-label", "Tags"
    h.input ".controls.tagsinput.input-xxlarge", type:"text", placeholder:"Tag names, comma separated"
    h.button ".btn.btn-primary.tag", type:'button', "Tag"
    h.br()
    h.button ".btn.btn-inverse.done.pull-right", type:'button', "I'm done"

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
    table_from_dict_partial: table_from_dict_partial
    one_col_table: one_col_table
    $one_col_table: $one_col_table
    table_from_dict: table_from_dict
    $table_from_dict: $table_from_dict
    one_submit: one_submit
    dropdown_submit: dropdown_submit
    one_submit_with_cb: one_submit_with_cb
    dropdown_submit_with_cb: dropdown_submit_with_cb
    link: link