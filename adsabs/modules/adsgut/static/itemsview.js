// Generated by CoffeeScript 1.6.1
(function() {
  var $, ItemView, ItemsFilterView, ItemsView, addwa, addwoa, addwoata, cdict, enval, h, prefix, remIndiv, remMulti, root, time_format, w,
    _this = this,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  h = teacup;

  w = widgets;

  prefix = GlobalVariables.ADS_PREFIX + '/adsgut';

  cdict = function(fqin, l) {
    var d;
    d = {};
    d[fqin] = l;
    return d;
  };

  enval = function(tag) {
    var ename, title, _ref;
    ename = encodeURIComponent(tag.text);
    if (!tag.url) {
      tag.url = "" + prefix + "/postable/" + this.memberable + "/group:default/filter/html?query=tagname:" + ename + "&query=tagtype:ads/tagtype:tag";
      title = (_ref = tag.title) != null ? _ref : ' data-toggle="tooltip" title="' + tag.title + {
        '"': ''
      };
      tag.id = tag.text;
      tag.text = '<a class="tag-link" ' + title + '" href="' + tag.url + '">' + tag.text + '</a>';
    }
    return tag;
  };

  addwa = function(tag, cback) {
    var eback,
      _this = this;
    eback = function(xhr, etext) {
      return alert('Did not succeed');
    };
    return syncs.submit_tag(this.item.basic.fqin, this.item.basic.name, tag.id, cback, eback);
  };

  addwoa = function(tag, cback) {
    this.update_tags(tag.id);
    return cback();
  };

  remIndiv = function(pill) {
    var tag;
    tag = $(pill).attr('data-tag-id');
    if (!this.tagajaxsubmit) {
      return this.remove_from_tags(tag);
    } else {

    }
  };

  time_format = function(timestring) {
    return timestring.split('.')[0].split('T').join(" at ");
  };

  ItemView = (function(_super) {

    __extends(ItemView, _super);

    function ItemView() {
      var _this = this;
      this.submitNote = function() {
        return ItemView.prototype.submitNote.apply(_this, arguments);
      };
      this.update_note_ajax = function(data) {
        return ItemView.prototype.update_note_ajax.apply(_this, arguments);
      };
      this.addToPostsView = function() {
        return ItemView.prototype.addToPostsView.apply(_this, arguments);
      };
      this.render = function() {
        return ItemView.prototype.render.apply(_this, arguments);
      };
      this.update_notes = function(newnotetuple) {
        return ItemView.prototype.update_notes.apply(_this, arguments);
      };
      this.update_posts = function(newposts) {
        return ItemView.prototype.update_posts.apply(_this, arguments);
      };
      this.remove_from_tags = function(newtag) {
        return ItemView.prototype.remove_from_tags.apply(_this, arguments);
      };
      this.update_tags = function(newtag) {
        return ItemView.prototype.update_tags.apply(_this, arguments);
      };
      this.update = function(postings, notes, tags) {
        return ItemView.prototype.update.apply(_this, arguments);
      };
      return ItemView.__super__.constructor.apply(this, arguments);
    }

    ItemView.prototype.tagName = 'div';

    ItemView.prototype.className = 'itemcontainer';

    ItemView.prototype.events = {
      "click .notebtn": "submitNote"
    };

    ItemView.prototype.initialize = function(options) {
      this.stags = options.stags, this.notes = options.notes, this.item = options.item, this.postings = options.postings, this.memberable = options.memberable, this.noteform = options.noteform, this.tagajaxsubmit = options.tagajaxsubmit, this.suggestions = options.suggestions, this.pview = options.pview;
      this.hv = void 0;
      this.newtags = [];
      this.newnotes = [];
      this.newposts = [];
      this.therebenotes = false;
      if (this.notes.length > 0) {
        return this.therebenotes = true;
      }
    };

    ItemView.prototype.update = function(postings, notes, tags) {
      this.stags = tags;
      this.notes = notes;
      return this.postings = postings;
    };

    ItemView.prototype.update_tags = function(newtag) {
      return this.newtags.push(newtag);
    };

    ItemView.prototype.remove_from_tags = function(newtag) {
      return this.newtags = _.without(this.newtags, newtag);
    };

    ItemView.prototype.update_posts = function(newposts) {
      return this.newposts = _.union(this.newposts, newposts);
    };

    ItemView.prototype.update_notes = function(newnotetuple) {
      return this.newnotes.push(newnotetuple);
    };

    ItemView.prototype.render = function() {
      var additional, additionalpostings, adslocation, content, fqin, htmlstring, jslist, tagdict, thepostings, thetags, url;
      this.$el.empty();
      adslocation = "http://labs.adsabs.harvard.edu/adsabs/abs/";
      url = adslocation + ("" + this.item.basic.name);
      if (this.item.whenposted) {
        htmlstring = "<div class='searchresultl'><a href=\"" + url + "\">" + this.item.basic.name + "</a>&nbsp;&nbsp;(saved " + (time_format(this.item.whenposted)) + ")</div>";
      } else {
        htmlstring = "<div class='searchresultl'><a href=\"" + url + "\">" + this.item.basic.name + "</a></div>";
      }
      fqin = this.item.basic.fqin;
      content = '';
      content = content + htmlstring;
      thetags = format_tags_for_item(fqin, cdict(fqin, this.stags), this.memberable);
      additional = "<span class='tagls'></span><br/>";
      thepostings = format_postings_for_item(fqin, cdict(fqin, this.postings), this.memberable);
      additionalpostings = "<strong>In Libraries</strong>: <span class='postls'>" + (thepostings.join(', ')) + "</span><br/>";
      additional = additional + additionalpostings;
      content = content + additional;
      this.$el.append(content);
      tagdict = {
        values: thetags,
        enhanceValue: _.bind(enval, this),
        addWithAjax: _.bind(addwa, this),
        addWithoutAjax: _.bind(addwoa, this),
        ajax_submit: this.tagajaxsubmit,
        onRemove: _.bind(remIndiv, this),
        suggestions: this.suggestions,
        templates: {
          pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
          add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">add tag</span>&nbsp;',
          input_pill: '<span></span>&nbsp;'
        }
      };
      jslist = [];
      this.$('.tagls').tags(jslist, tagdict);
      this.tagsobject = jslist[0];
      if (this.noteform) {
        this.hv = new w.HideableView({
          state: 0,
          widget: w.postalnote_form("make note", 2, this.pview),
          theclass: ".postalnote"
        });
        this.$el.append(this.hv.render("<strong>Notes</strong>: ").$el);
        if (this.hv.state === 0) {
          this.hv.hide();
        }
        if (this.therebenotes) {
          this.$el.append("<p class='notes'></p>");
          this.$('.notes').append(format_notes_for_item(fqin, cdict(fqin, this.notes), this.memberable));
        }
      }
      return this;
    };

    ItemView.prototype.addToPostsView = function() {
      var already, fqin, inbet, p, poststoshow, thepostings;
      fqin = this.item.basic.fqin;
      poststoshow = (function() {
        var _i, _len, _ref, _results;
        _ref = this.newposts;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          p = _ref[_i];
          if (__indexOf.call(this.postings, p) < 0) {
            _results.push(p);
          }
        }
        return _results;
      }).call(this);
      thepostings = format_postings_for_item(fqin, cdict(fqin, poststoshow), this.memberable);
      already = format_postings_for_item(fqin, cdict(fqin, this.postings), this.memberable).join(', ');
      inbet = '';
      if (already !== '') {
        inbet = ', ';
      }
      return this.$('.postls').html(already + inbet + thepostings.join(', '));
    };

    ItemView.prototype.update_note_ajax = function(data) {
      var fqin, notes, stags, _ref;
      fqin = this.item.basic.fqin;
      _ref = get_taggings(data), stags = _ref[0], notes = _ref[1];
      this.stags = stags[fqin];
      this.notes = notes[fqin];
      this.therebenotes = true;
      return this.render();
    };

    ItemView.prototype.submitNote = function() {
      var cback, eback, item, itemname, loc, notemode, notetext,
        _this = this;
      item = this.item.basic.fqin;
      itemname = this.item.basic.name;
      notetext = this.$('.txt').val();
      notemode = '1';
      if (this.$('.cb').is(':checked')) {
        if (this.pview === 'pub') {
          notemode = '0';
        } else if (this.pview === 'udg' || this.pview === 'none') {
          notemode = '0';
        } else {
          notemode = this.pview;
        }
      }
      loc = window.location;
      cback = function(data) {
        return _this.update_note_ajax(data);
      };
      eback = function(xhr, etext) {
        return alert('Did not succeed');
      };
      if (this.tagajaxsubmit) {
        syncs.submit_note(item, itemname, [notetext, notemode], cback, eback);
      } else {
        this.update_notes([notetext, notemode]);
        if (!this.therebenotes) {
          this.$el.append("<p class='notes'></p>");
          this.therebenotes = true;
        }
        this.$('.notes').prepend("<span>" + notetext + "</span><br/>");
        this.hv.hide();
        this.$('.txt').val("");
      }
      return false;
    };

    return ItemView;

  })(Backbone.View);

  addwoata = function(tag, cback) {
    this.update_tags(tag);
    return cback();
  };

  remMulti = function(pill) {
    var fqin, i, tag, _i, _len, _ref, _results;
    tag = $(pill).attr('data-tag-id');
    if (!this.tagajaxsubmit) {
      _ref = this.items;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        _results.push(this.itemviews[fqin].tagsobject.removeTag(this.itemviews[fqin].$("[data-tag-id='" + tag + "']")));
      }
      return _results;
    } else {

    }
  };

  ItemsView = (function(_super) {

    __extends(ItemsView, _super);

    function ItemsView() {
      var _this = this;
      this.submitTags = function() {
        return ItemsView.prototype.submitTags.apply(_this, arguments);
      };
      this.collectPosts = function() {
        return ItemsView.prototype.collectPosts.apply(_this, arguments);
      };
      this.collectNotes = function() {
        return ItemsView.prototype.collectNotes.apply(_this, arguments);
      };
      this.collectTags = function() {
        return ItemsView.prototype.collectTags.apply(_this, arguments);
      };
      this.submitPosts = function() {
        return ItemsView.prototype.submitPosts.apply(_this, arguments);
      };
      this.iDone = function() {
        return ItemsView.prototype.iDone.apply(_this, arguments);
      };
      this.iCancel = function() {
        return ItemsView.prototype.iCancel.apply(_this, arguments);
      };
      this.render = function() {
        return ItemsView.prototype.render.apply(_this, arguments);
      };
      this.update_posts = function(postables) {
        return ItemsView.prototype.update_posts.apply(_this, arguments);
      };
      this.update_tags = function(newtag) {
        return ItemsView.prototype.update_tags.apply(_this, arguments);
      };
      this.update_postings_taggings = function() {
        return ItemsView.prototype.update_postings_taggings.apply(_this, arguments);
      };
      return ItemsView.__super__.constructor.apply(this, arguments);
    }

    ItemsView.prototype.events = {
      "click .post": "submitPosts",
      "click .tag": "submitTags",
      "click .done": "iDone",
      "click .cancel": "iCancel"
    };

    ItemsView.prototype.initialize = function(options) {
      this.stags = options.stags, this.notes = options.notes, this.$el = options.$el, this.postings = options.postings, this.memberable = options.memberable, this.items = options.items, this.nameable = options.nameable, this.itemtype = options.itemtype, this.loc = options.loc, this.noteform = options.noteform, this.suggestions = options.suggestions, this.pview = options.pview;
      this.newposts = [];
      return this.tagajaxsubmit = false;
    };

    ItemsView.prototype.update_postings_taggings = function() {
      var i, itemlist, itemsq,
        _this = this;
      this.postings = {};
      itemlist = (function() {
        var _i, _len, _ref, _results;
        _ref = this.items;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push("items=" + (encodeURIComponent(i.basic.fqin)));
        }
        return _results;
      }).call(this);
      itemsq = itemlist.join("&");
      return $.get(prefix + ("/items/taggingsandpostings?" + itemsq), function(data) {
        var e, fqin, k, v, _i, _len, _ref, _ref1, _ref2, _results;
        _ref = get_taggings(data), _this.stags = _ref[0], _this.notes = _ref[1];
        _ref1 = data.postings;
        for (k in _ref1) {
          if (!__hasProp.call(_ref1, k)) continue;
          v = _ref1[k];
          if (v[0] > 0) {
            _this.postings[k] = (function() {
              var _i, _len, _ref2, _results;
              _ref2 = v[1];
              _results = [];
              for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
                e = _ref2[_i];
                _results.push(e.posting.postfqin);
              }
              return _results;
            })();
          } else {
            _this.postings[k] = [];
          }
        }
        _ref2 = _this.items;
        _results = [];
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
          i = _ref2[_i];
          fqin = i.basic.fqin;
          _this.itemviews[fqin].update(_this.postings[fqin], _this.notes[fqin], _this.stags[fqin]);
          _results.push(_this.itemviews[fqin].render());
        }
        return _results;
      });
    };

    ItemsView.prototype.update_tags = function(newtag) {
      var fqin, i, _i, _len, _ref, _results;
      _ref = this.items;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        _results.push(this.itemviews[fqin].tagsobject.addTag(this.itemviews[fqin].$('.pills-list'), newtag));
      }
      return _results;
    };

    ItemsView.prototype.update_posts = function(postables) {
      var fqin, i, p, _i, _j, _len, _len1, _ref, _results;
      for (_i = 0, _len = postables.length; _i < _len; _i++) {
        p = postables[_i];
        this.newposts = _.union(this.newposts, postables);
      }
      _ref = this.items;
      _results = [];
      for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
        i = _ref[_j];
        fqin = i.basic.fqin;
        this.itemviews[fqin].update_posts(this.newposts);
        _results.push(this.itemviews[fqin].addToPostsView());
      }
      return _results;
    };

    ItemsView.prototype.render = function() {
      var $ctrls, $lister, cback, eback, fqin, i, ins, v, _i, _len, _ref,
        _this = this;
      $lister = this.$('.items');
      $ctrls = this.$('.ctrls');
      this.itemviews = {};
      _ref = this.items;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        ins = {
          stags: this.stags[fqin],
          notes: this.notes[fqin],
          postings: this.postings[fqin],
          item: i,
          memberable: this.memberable,
          noteform: this.noteform,
          tagajaxsubmit: this.tagajaxsubmit,
          suggestions: this.suggestions,
          pview: this.pview
        };
        v = new ItemView(ins);
        $lister.append(v.render().el);
        this.itemviews[fqin] = v;
      }
      eback = function(xhr, etext) {
        return alert('Did not succeed');
      };
      cback = function(data) {
        var jslist, libs, tagdict;
        libs = _.union(data.libraries, data.groups);
        $ctrls.append(w.postalall_form(_this.nameable, _this.itemtype, libs));
        tagdict = {
          enhanceValue: _.bind(enval, _this),
          addWithAjax: _.bind(addwa, _this),
          addWithoutAjax: _.bind(addwoata, _this),
          ajax_submit: false,
          onRemove: _.bind(remMulti, _this),
          suggestions: _this.suggestions,
          templates: {
            pill: '<span class="badge badge-default tag-badge" style="margin-right:3px;">{0}</span>&nbsp;&nbsp;&nbsp;&nbsp;',
            add_pill: '<span class="label label-info tag-badge" style="margin-right:3px;margin-left:7px;">add tag</span>&nbsp;',
            input_pill: '<span></span>&nbsp;'
          }
        };
        jslist = [];
        _this.$('#alltags').tags(jslist, tagdict);
        _this.$('.multilibrary').multiselect({
          includeSelectAllOption: true,
          enableFiltering: true,
          maxHeight: 150
        });
        return _this.globaltagsobject = jslist[0];
      };
      syncs.get_postables_writable(this.memberable, cback, eback);
      return this;
    };

    ItemsView.prototype.iCancel = function() {
      return $.fancybox.close();
    };

    ItemsView.prototype.iDone = function() {
      var cback, cback_notes, cback_posts, cback_tags, eback, ns, postables, ts,
        _this = this;
      cback = function(data) {
        return $.fancybox.close();
      };
      eback = function(xhr, etext) {
        return alert('Did not succeed');
      };
      postables = this.collectPosts();
      ts = this.collectTags();
      ns = this.collectNotes();
      cback_notes = function() {
        return syncs.submit_notes(_this.items, ns, cback, eback);
      };
      cback_tags = function() {
        return syncs.submit_tags(_this.items, ts, cback_notes, eback);
      };
      cback_posts = function() {
        return syncs.submit_posts(_this.items, postables, cback_tags, eback);
      };
      syncs.save_items(this.items, cback_posts, eback);
      return false;
    };

    ItemsView.prototype.submitPosts = function() {
      var cback, eback, libs, loc, postables,
        _this = this;
      libs = this.$('.multilibrary').val();
      if (libs === null) {
        libs = [];
      }
      postables = _.without(libs, 'multiselect-all');
      $('option', this.$('.multilibrary')).each(function(ele) {
        return $(this).removeAttr('selected').prop('selected', false);
      });
      this.$('.multilibrary').multiselect('refresh');
      loc = window.location;
      cback = function(data) {
        return _this.update_postings_taggings();
      };
      eback = function(xhr, etext) {
        return alert('Did not succeed saving to libraries');
      };
      if (this.tagajaxsubmit) {
        syncs.submit_posts(this.items, postables, cback, eback);
      } else {
        this.update_posts(postables);
      }
      return false;
    };

    ItemsView.prototype.collectTags = function() {
      var e, fqin, i, iview, ntags, tags, _i, _len, _ref;
      tags = {};
      _ref = this.items;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        iview = this.itemviews[fqin];
        ntags = iview.newtags;
        tags[fqin] = (function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = ntags.length; _j < _len1; _j++) {
            e = ntags[_j];
            if (e !== "") {
              _results.push(e.trim());
            }
          }
          return _results;
        })();
      }
      return tags;
    };

    ItemsView.prototype.collectNotes = function() {
      var e, fqin, i, iview, notes, ntags, _i, _len, _ref;
      notes = {};
      _ref = this.items;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        iview = this.itemviews[fqin];
        if (iview.therebenotes) {
          ntags = iview.newnotes;
        } else {
          ntags = [];
        }
        notes[fqin] = (function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = ntags.length; _j < _len1; _j++) {
            e = ntags[_j];
            if (e[0] !== "") {
              _results.push([e[0].trim(), e[1]]);
            }
          }
          return _results;
        })();
      }
      return notes;
    };

    ItemsView.prototype.collectPosts = function() {
      return this.newposts;
    };

    ItemsView.prototype.submitTags = function() {
      var cback, e, eback, fqin, i, loc, tags, tagstring, ts, _i, _len, _ref,
        _this = this;
      ts = {};
      tagstring = this.$('.tagsinput').val();
      if (tagstring === "") {
        tags = [];
      } else {
        tags = (function() {
          var _i, _len, _ref, _results;
          _ref = tagstring.split(',');
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            e = _ref[_i];
            _results.push(e.trim());
          }
          return _results;
        })();
        tags = (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = tags.length; _i < _len; _i++) {
            e = tags[_i];
            if (e !== "") {
              _results.push(e);
            }
          }
          return _results;
        })();
      }
      loc = window.location;
      _ref = this.items;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        ts[fqin] = tags;
      }
      cback = function(data) {
        return _this.update_postings_taggings();
      };
      eback = function(xhr, etext) {
        return alert('Did not succeed tagging');
      };
      syncs.submit_tags(this.items, ts, cback, eback);
      return false;
    };

    return ItemsView;

  })(Backbone.View);

  ItemsFilterView = (function(_super) {

    __extends(ItemsFilterView, _super);

    function ItemsFilterView() {
      var _this = this;
      this.render = function() {
        return ItemsFilterView.prototype.render.apply(_this, arguments);
      };
      return ItemsFilterView.__super__.constructor.apply(this, arguments);
    }

    ItemsFilterView.prototype.initialize = function(options) {
      return this.stags = options.stags, this.notes = options.notes, this.$el = options.$el, this.postings = options.postings, this.memberable = options.memberable, this.items = options.items, this.nameable = options.nameable, this.itemtype = options.itemtype, this.noteform = options.noteform, this.suggestions = options.suggestions, this.pview = options.pview, options;
    };

    ItemsFilterView.prototype.render = function() {
      var fqin, i, ins, v, _i, _len, _ref;
      this.itemviews = {};
      _ref = this.items;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        fqin = i.basic.fqin;
        ins = {
          stags: this.stags[fqin],
          notes: this.notes[fqin],
          postings: this.postings[fqin],
          item: i,
          memberable: this.memberable,
          noteform: this.noteform,
          tagajaxsubmit: true,
          suggestions: this.suggestions,
          pview: this.pview
        };
        v = new ItemView(ins);
        this.$el.append(v.render().el);
        this.itemviews[fqin] = v;
        this.$el.append('<hr/>');
      }
      return this;
    };

    return ItemsFilterView;

  })(Backbone.View);

  root.itemsdo = {
    ItemView: ItemView,
    ItemsView: ItemsView,
    ItemsFilterView: ItemsFilterView
  };

}).call(this);
