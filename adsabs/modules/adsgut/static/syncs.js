// Generated by CoffeeScript 1.6.1

/*
the idea behind syncs.coffee is to create a Backbone sync component for our API.
For this we must identify the models and views across our pages.

The method signature of Backbone.sync is sync(method, model, [options])

method – the CRUD method ("create", "read", "update", or "delete")
model – the model to be saved (or collection to be read)
options – success and error callbacks, and all other jQuery request options

With the default implementation, when Backbone.sync sends up a request to save a model, 
its attributes will be passed, serialized as JSON, and sent in the HTTP body with content-type application/json. 
When returning a JSON response, send down the attributes of the model that have been changed by the server, 
and need to be updated on the client. When responding to a "read" request from a collection (Collection#fetch), 
send down an array of model attribute objects.

Whenever a model or collection begins a sync with the server, a "request" event is emitted. 
If the request completes successfully you'll get a "sync" event, and an "error" event if not.

The sync function may be overriden globally as Backbone.sync, or at a finer-grained level, 
by adding a sync function to a Backbone collection or to an individual model.

#but we shall first start slow, by building in direct jquery functions here, instead of Backbone.sync.
This will document the api as well. We wont start with gets, but remember we want to later put gets inside
collections.fetch

error
Type: Function( jqXHR jqXHR, String textStatus, String errorThrown )
success
Type: Function( PlainObject data, String textStatus, jqXHR jqXHR )
*/


(function() {
  var $, accept_invitation, add_group, change_description, change_ownership, create_postable, do_get, doajax, get_postables, get_postables_writable, h, invite_user, prefix, root, save_items, send_bibcodes, send_params, submit_note, submit_notes, submit_posts, submit_tag, submit_tags, toggle_rw;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  console.log("In Funcs");

  h = teacup;

  doajax = $.ajax;

  prefix = GlobalVariables.ADS_PREFIX + "/adsgut";

  send_params = function(url, data, cback, eback) {
    var params, stringydata, xhr;
    stringydata = JSON.stringify(data);
    params = {
      type: 'POST',
      dataType: 'json',
      url: url,
      data: stringydata,
      contentType: "application/json",
      success: cback,
      error: eback
    };
    return xhr = doajax(params);
  };

  send_bibcodes = function(url, items, cback, eback) {
    var bibcodes, data, i;
    bibcodes = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        i = items[_i];
        _results.push(i.basic.name);
      }
      return _results;
    })();
    data = {
      bibcode: bibcodes
    };
    console.log("SBDATA", data);
    return send_params(url, data, cback, eback);
  };

  do_get = function(url, cback, eback) {
    var params, xhr;
    params = {
      type: 'GET',
      dataType: 'json',
      url: url,
      success: cback,
      error: eback
    };
    return xhr = doajax(params);
  };

  change_ownership = function(adsid, fqpn, cback, eback) {
    var data, url;
    url = prefix + "/postable/" + fqpn + "/changes";
    data = {
      memberable: adsid,
      op: 'changeowner'
    };
    return send_params(url, data, cback, eback);
  };

  toggle_rw = function(fqmn, fqpn, cback, eback) {
    var data, url;
    url = prefix + "/postable/" + fqpn + "/changes";
    data = {
      memberable: fqmn,
      op: 'togglerw'
    };
    return send_params(url, data, cback, eback);
  };

  change_description = function(description, fqpn, cback, eback) {
    var data, url;
    url = prefix + "/postable/" + fqpn + "/changes";
    data = {
      memberable: "crap",
      op: 'description',
      description: description
    };
    return send_params(url, data, cback, eback);
  };

  accept_invitation = function(adsid, fqpn, cback, eback) {
    var data, url;
    url = prefix + "/postable/" + fqpn + "/changes";
    data = {
      memberable: adsid,
      op: 'accept'
    };
    return send_params(url, data, cback, eback);
  };

  invite_user = function(adsid, postable, changerw, cback, eback) {
    var data, url;
    url = prefix + "/postable/" + postable + "/changes";
    data = {
      memberable: adsid,
      op: 'invite',
      changerw: changerw
    };
    return send_params(url, data, cback, eback);
  };

  create_postable = function(postable, postabletype, cback, eback) {
    var data, url;
    url = prefix + ("/" + postabletype);
    data = {
      name: postable.name,
      description: postable.description
    };
    return send_params(url, data, cback, eback);
  };

  add_group = function(selectedgrp, postable, changerw, cback, eback) {
    var data, url;
    url = prefix + "/postable/" + postable + "/members";
    data = {
      member: selectedgrp,
      changerw: changerw
    };
    return send_params(url, data, cback, eback);
  };

  get_postables = function(user, cback, eback) {
    var nick, url;
    nick = user;
    url = prefix + "/user/" + nick + "/postablesuserisin";
    return do_get(url, cback, eback);
  };

  get_postables_writable = function(user, cback, eback) {
    var nick, url;
    nick = user;
    url = prefix + "/user/" + nick + "/postablesusercanwriteto";
    return do_get(url, cback, eback);
  };

  submit_note = function(item, itemname, notetuple, cback, eback) {
    var data, itemtype, tagtype, ts, url;
    tagtype = "ads/tagtype:note";
    itemtype = "ads/itemtype:pub";
    url = prefix + "/tags/" + item;
    ts = {};
    ts[itemname] = [
      {
        content: notetuple[0],
        tagtype: tagtype,
        tagmode: notetuple[1]
      }
    ];
    data = {
      tagspecs: ts,
      itemtype: itemtype
    };
    if (notetuple[0] !== "") {
      return send_params(url, data, cback, eback);
    }
  };

  submit_tag = function(item, itemname, tag, cback, eback) {
    var data, itemtype, tagtype, ts, url;
    tagtype = "ads/tagtype:tag";
    itemtype = "ads/itemtype:pub";
    url = prefix + "/tags/" + item;
    ts = {};
    ts[itemname] = [
      {
        name: tag,
        tagtype: tagtype
      }
    ];
    data = {
      tagspecs: ts,
      itemtype: itemtype
    };
    if (tag !== "") {
      return send_params(url, data, cback, eback);
    }
  };

  submit_tags = function(items, tags, cback, eback) {
    var data, fqin, i, inames, itemtype, name, t, tagtype, ts, url, _i, _len;
    tagtype = "ads/tagtype:tag";
    itemtype = "ads/itemtype:pub";
    url = prefix + "/items/taggings";
    console.log("TAGS ARE", tags);
    ts = {};
    inames = [];
    for (_i = 0, _len = items.length; _i < _len; _i++) {
      i = items[_i];
      fqin = i.basic.fqin;
      name = i.basic.name;
      if (tags[fqin].length > 0) {
        inames.push(name);
        ts[name] = (function() {
          var _j, _len1, _ref, _results;
          _ref = tags[fqin];
          _results = [];
          for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
            t = _ref[_j];
            _results.push({
              name: t,
              tagtype: tagtype
            });
          }
          return _results;
        })();
      }
    }
    if (inames.length > 0) {
      data = {
        tagspecs: ts,
        itemtype: itemtype,
        items: inames
      };
      return send_params(url, data, cback, eback);
    } else {
      return cback();
    }
  };

  submit_notes = function(items, notetuples, cback, eback) {
    var data, fqin, i, inames, itemtype, name, nt, tagtype, ts, url, _i, _len;
    tagtype = "ads/tagtype:note";
    itemtype = "ads/itemtype:pub";
    url = prefix + "/items/taggings";
    ts = {};
    inames = [];
    for (_i = 0, _len = items.length; _i < _len; _i++) {
      i = items[_i];
      fqin = i.basic.fqin;
      name = i.basic.name;
      if (notetuples[fqin].length > 0) {
        inames.push(name);
        ts[name] = (function() {
          var _j, _len1, _ref, _results;
          _ref = notetuples[fqin];
          _results = [];
          for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
            nt = _ref[_j];
            _results.push({
              content: nt[0],
              tagtype: tagtype,
              tagmode: nt[1]
            });
          }
          return _results;
        })();
      }
    }
    if (inames.length > 0) {
      data = {
        tagspecs: ts,
        itemtype: itemtype,
        items: inames
      };
      return send_params(url, data, cback, eback);
    } else {
      return cback();
    }
  };

  submit_posts = function(items, postables, cback, eback) {
    var data, i, itemnames, itemtype, url;
    itemtype = "ads/itemtype:pub";
    console.log(items, '|||', postables);
    itemnames = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        i = items[_i];
        _results.push(i.basic.name);
      }
      return _results;
    })();
    url = prefix + "/items/postings";
    if (postables.length > 0) {
      data = {
        postables: postables,
        itemtype: itemtype,
        items: itemnames
      };
      return send_params(url, data, cback, eback);
    } else {
      return cback();
    }
  };

  save_items = function(items, cback, eback) {
    var data, i, itemnames, itemtype, url;
    itemtype = "ads/itemtype:pub";
    console.log(items, '|||');
    itemnames = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        i = items[_i];
        _results.push(i.basic.name);
      }
      return _results;
    })();
    url = prefix + "/items";
    data = {
      items: itemnames,
      itemtype: itemtype
    };
    return send_params(url, data, cback, eback);
  };

  root.syncs = {
    accept_invitation: accept_invitation,
    invite_user: invite_user,
    add_group: add_group,
    change_ownership: change_ownership,
    toggle_rw: toggle_rw,
    get_postables: get_postables,
    get_postables_writable: get_postables_writable,
    submit_note: submit_note,
    submit_tag: submit_tag,
    submit_tags: submit_tags,
    submit_notes: submit_notes,
    submit_posts: submit_posts,
    save_items: save_items,
    create_postable: create_postable,
    change_description: change_description,
    send_bibcodes: send_bibcodes
  };

}).call(this);
