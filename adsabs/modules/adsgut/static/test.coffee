Backbone=require('./backbone')
teacup=require('./teacup')
class Postable extends Backbone.Model


class PostableList extends Backbone.Collection
    
    model: Postable 
    initialize: (mod, opt) ->
        @listtype=opt.listtype
        @invite=opt.invite


A=['a', 'b']
pl=new PostableList([], {listtype:'in', invite: false})
pl.add((new Postable({fqpn:p, invite:pl.invite}) for p in A))
console.log "GG", pl
console.log "FF", p.get('fqpn') for p in pl.models

out = teacup.render ->
    teacup.raw "ram"

out2= teacup.h1 "hello"
console.log ">>",out,"<<",typeof out, out2, typeof out2
a=
    a:1
    b:2

console.log (u for u of a)
