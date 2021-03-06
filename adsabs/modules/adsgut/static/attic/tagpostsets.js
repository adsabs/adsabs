// Generated by CoffeeScript 1.6.1
(function() {
  var $, TagsetView, h, prefix, root, w,
    _this = this,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  console.log("In Funcs");

  h = teacup;

  w = widgets;

  prefix = GlobalVariables.ADS_PREFIX + "/adsgut";

  ({
    update_postings_taggings: function() {
      var i, itemlist, itemsq;
      _this.postings = {};
      console.log("itys", _this.items);
      itemlist = (function() {
        var _i, _len, _ref, _results;
        _ref = this.items;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push("items=" + (encodeURIComponent(i.basic.fqin)));
        }
        return _results;
      }).call(_this);
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
                _results.push(e.thething.postfqin);
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
    }
  });

  TagsetView = (function(_super) {

    __extends(TagsetView, _super);

    function TagsetView() {
      var _this = this;
      this.submitTags = function() {
        return TagsetView.prototype.submitTags.apply(_this, arguments);
      };
      this.submitPosts = function() {
        return TagsetView.prototype.submitPosts.apply(_this, arguments);
      };
      this.iDone = function() {
        return TagsetView.prototype.iDone.apply(_this, arguments);
      };
      this.render = function() {
        return TagsetView.prototype.render.apply(_this, arguments);
      };
      return TagsetView.__super__.constructor.apply(this, arguments);
    }

    TagsetView.prototype.events = {
      "click .tag": "submitTags",
      "click .done": "iDone"
    };

    TagsetView.prototype.initialize = function(options) {
      return this.stags = options.stags, this.$el = options.$el, this.memberable = options.memberable, this.items = options.items, this.nameable = options.nameable, this.itemtype = options.itemtype, this.loc = options.loc, this.noteform = options.noteform, options;
    };

    TagsetView.prototype.render = function() {
      var $ctrls, $lister, cback, eback, fqin, i, ins, v, _i, _len, _ref,
        _this = this;
      $lister = this.$el;
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
          noteform: this.noteform
        };
        v = new ItemView(ins);
        $lister.append(v.render().el);
        this.itemviews[fqin] = v;
      }
      eback = function(xhr, etext) {
        console.log("ERROR", etext);
        return alert('Did not succeed');
      };
      cback = function(data) {
        var libs;
        console.log(data);
        libs = _.union(data.libraries, data.groups);
        return $ctrls.append(w.postalall_form(_this.nameable, _this.itemtype, libs));
      };
      syncs.get_postables_writable(this.memberable, cback, eback);
      return this;
    };

    TagsetView.prototype.iDone = function() {
      var cback, eback,
        _this = this;
      cback = function(data) {
        return window.location = _this.loc;
      };
      eback = function(xhr, etext) {
        console.log("ERROR", etext, _this.loc);
        return alert('Did not succeed');
      };
      syncs.save_items(this.items, cback, eback);
      window.close();
      return false;
    };

    TagsetView.prototype.submitPosts = function() {
      var cback, eback, libs, loc, makepublic, postables,
        _this = this;
      libs = this.$('.multilibrary').val();
      if (libs === null) {
        libs = [];
      }
      postables = libs;
      makepublic = this.$('.makepublic').is(':checked');
      if (makepublic) {
        postables = postables.concat(['adsgut/group:public']);
      }
      loc = window.location;
      cback = function(data) {
        return _this.update_postings_taggings();
      };
      eback = function(xhr, etext) {
        console.log("ERROR", etext, loc);
        return alert('Did not succeed');
      };
      syncs.submit_posts(this.items, postables, cback, eback);
      return false;
    };

    TagsetView.prototype.submitTags = function() {
      var cback, e, eback, loc, tags, tagstring,
        _this = this;
      tagstring = this.$('.tagsinput').val();
      if (tagstring === "") {
        console.log("a");
        tags = [];
      } else {
        console.log("b", (function() {
          var _i, _len, _ref, _results;
          _ref = tagstring.split(',');
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            e = _ref[_i];
            _results.push(e);
          }
          return _results;
        })());
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
      cback = function(data) {
        _this.$('.tagsinput').val("");
        return _this.update_postings_taggings();
      };
      eback = function(xhr, etext) {
        console.log("ERROR", etext, loc);
        return alert('Did not succeed');
      };
      syncs.submit_tags(this.items, tags, cback, eback);
      return false;
    };

    return TagsetView;

  })(Backbone.View);

  root.tpsets = {
    TagsetView: TagsetView
  };

}).call(this);
