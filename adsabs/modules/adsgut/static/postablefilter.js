// Generated by CoffeeScript 1.7.1
(function() {
  var $, csvstringify, do_postable_filter, do_postable_info, do_tags, flip_sorter, h, make_editable_description, parse_querystring, root,
    __hasProp = {}.hasOwnProperty,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  h = teacup;

  flip_sorter = function(qstr) {
    var a, anowtext, aout, atext, f, fnowtext, fout, ftext, n, odict, otherqlist, q, qlist, sortstring, _i, _len, _ref;
    qlist = qstr.split('&');
    sortstring = "";
    otherqlist = [];
    for (_i = 0, _len = qlist.length; _i < _len; _i++) {
      q = qlist[_i];
      n = q.search("sort");
      if (n === 0) {
        sortstring = q.split('=')[1];
      } else {
        otherqlist.push(q);
      }
    }
    if (sortstring !== '') {
      _ref = sortstring.split(':'), f = _ref[0], a = _ref[1];
      if (f === 'posting__thingtopostname') {
        fnowtext = "by paper year";
        ftext = 'Sort By Post';
        fout = 'posting__whenposted';
      }
      if (f === 'posting__whenposted') {
        fnowtext = "by posting time";
        ftext = 'Sort By Year';
        fout = 'posting__thingtopostname';
      }
      if (a === 'True') {
        anowtext = "earliest first";
        atext = '<i class="icon-arrow-down"></i>';
        aout = 'False';
      }
      if (a === 'False') {
        anowtext = "latest first";
        atext = '<i class="icon-arrow-up"></i>';
        aout = 'True';
      }
    } else {
      f = 'posting__whenposted';
      a = 'False';
      fnowtext = "by posting time";
      anowtext = "latest first";
      ftext = 'Sort By Year';
      atext = '<i class="icon-arrow-up"></i>';
      fout = 'posting__thingtopostname';
      aout = 'True';
    }
    odict = {
      fnow: f,
      anow: a,
      fnowtext: fnowtext,
      anowtext: anowtext,
      ftext: ftext,
      atext: atext,
      fout: fout,
      aout: aout,
      oqs: otherqlist.join('&')
    };
    return odict;
  };

  csvstringify = function(tdict) {
    var bibcode, start, tag, _i, _len, _ref;
    start = "#paper, tag\n";
    for (bibcode in tdict) {
      _ref = tdict[bibcode];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        tag = _ref[_i];
        start = start + bibcode + "," + tag + "\n";
      }
    }
    return start;
  };

  parse_querystring = function(qstr) {
    var n, q, q2list, qlist, _i, _len;
    qlist = qstr.split('&');
    qlist = _.difference(qlist, ['query=tagtype:ads/tagtype:tag']);
    qlist = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = qlist.length; _i < _len; _i++) {
        q = qlist[_i];
        _results.push(q.replace('query=tagname:', ''));
      }
      return _results;
    })();
    q2list = [];
    for (_i = 0, _len = qlist.length; _i < _len; _i++) {
      q = qlist[_i];
      n = q.search("sort");
      if (n !== 0) {
        q2list.push(q);
      }
    }
    if (q2list.length === 1 && q2list[0] === "") {
      q2list = [];
    }
    return q2list;
  };

  make_editable_description = function($infodiv, fqpn) {
    var cback, eback;
    cback = function() {};
    eback = function() {};
    $.fn.editable.defaults.mode = 'inline';
    $infodiv.find('.edtext').editable({
      type: 'textarea',
      rows: 2,
      url: function(params) {
        return syncs.change_description(params.value, fqpn, cback, eback);
      }
    });
    return $infodiv.find('.edclick').click(function(e) {
      e.stopPropagation();
      e.preventDefault();
      return $infodiv.find('.edtext').editable('toggle');
    });
  };

  do_postable_info = function(sections, config, ptype) {
    return $.get(config.infoURL, function(data) {
      var content;
      if (ptype === 'library') {
        content = views.library_info(config.owner, data, templates.library_itemsinfo);
      } else if (ptype === 'group') {
        content = views.group_info(config.owner, data, templates.group_itemsinfo);
      }
      sections.$info.append(content + '<hr/>');
      if (config.owner) {
        make_editable_description(sections.$info, config.fqpn);
      }
      return sections.$info.show();
    });
  };

  do_tags = function(url, $sel, tqtype) {
    return $.get(url, function(data) {
      var k, v, _ref, _results;
      _ref = data.tags;
      _results = [];
      for (k in _ref) {
        if (!__hasProp.call(_ref, k)) continue;
        v = _ref[k];
        _results.push(format_tags(k, $sel, get_tags(v, tqtype), tqtype));
      }
      return _results;
    });
  };

  do_postable_filter = function(sections, config, tagfunc) {
    var loc, nonqloc, sortdict, urla;
    tagfunc();
    $.get("" + config.tagsucwtURL + "?tagtype=ads/tagtype:tag", function(data) {
      var e, qtxtlist, suggestions, _i, _len;
      suggestions = data.simpletags;
      qtxtlist = parse_querystring(config.querystring);
      if (qtxtlist.length > 0) {
        sections.$breadcrumb.text('Tags: ');
        for (_i = 0, _len = qtxtlist.length; _i < _len; _i++) {
          e = qtxtlist[_i];
          if (e === "userthere=true") {
            e = "Posted by you";
          }
          sections.$breadcrumb.append("<span class='badge'>" + e + "</span>&nbsp;");
        }
        sections.$breadcrumb.show();
      }
      return $.get(config.itemsPURL, function(data) {
        var biblist, bibstring, i, itemlist, itemsq, thecount, theitems;
        theitems = data.items;
        if (theitems.length === 1) {
          sections.$count.text("" + theitems.length + " paper. ");
        } else {
          sections.$count.text("" + theitems.length + " papers. ");
        }
        sections.$count.show();
        thecount = data.count;
        itemlist = (function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = theitems.length; _j < _len1; _j++) {
            i = theitems[_j];
            _results.push(i.basic.fqin);
          }
          return _results;
        })();
        biblist = (function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = theitems.length; _j < _len1; _j++) {
            i = theitems[_j];
            _results.push(i.basic.name);
          }
          return _results;
        })();
        bibstring = biblist.join("\n");
        sections.$bigquery.val(bibstring);
        sections.$bigqueryform.attr("action", config.bq2url);
        itemsq = itemlist.join("&");
        return syncs.taggings_postings_post_get(itemlist, config.pview, function(data) {
          var cb, clist, eb, ido, k, notes, plinv, postings, prop, sorteditems, stags, tagoutput, times, v, _j, _k, _len1, _len2, _ref, _ref1, _ref2, _ref3;
          _ref = get_taggings(data), stags = _ref[0], notes = _ref[1];
          tagoutput = {};
          for (prop in stags) {
            clist = stags[prop];
            if (clist.length === 0) {
              tagoutput[prop] = [];
            } else {
              tagoutput[prop] = (function() {
                var _j, _len1, _results;
                _results = [];
                for (_j = 0, _len1 = clist.length; _j < _len1; _j++) {
                  e = clist[_j];
                  _results.push(e[0]);
                }
                return _results;
              })();
            }
          }
          sections.$asjson.click(function(e) {
            window.location.href = config.jsonPURL;
            return e.preventDefault();
          });
          sections.$ascsv.click(function(e) {
            window.location.href = config.csvPURL;
            return e.preventDefault();
          });
          postings = {};
          times = {};
          _ref1 = data.postings;
          for (k in _ref1) {
            if (!__hasProp.call(_ref1, k)) continue;
            v = _ref1[k];
            if (v[0] > 0) {
              postings[k] = [];
              _ref2 = v[1];
              for (_j = 0, _len1 = _ref2.length; _j < _len1; _j++) {
                e = _ref2[_j];
                if (e.hist.length > 1) {
                  _ref3 = e.hist;
                  for (_k = 0, _len2 = _ref3.length; _k < _len2; _k++) {
                    h = _ref3[_k];
                    postings[k].push([e.posting.postfqin, h.postedby]);
                  }
                } else {
                  postings[k].push([e.posting.postfqin, e.posting.postedby]);
                }
              }
            } else {
              postings[k] = [];
            }
          }
          sorteditems = theitems;
          ido = {
            stags: stags,
            postings: postings,
            notes: notes,
            $el: sections.$items,
            items: sorteditems,
            noteform: true,
            nameable: false,
            itemtype: 'ads/pub',
            memberable: config.memberable,
            suggestions: suggestions,
            pview: config.pview,
            pviewowner: config.owner,
            pviewrw: config.rw,
            tagfunc: tagfunc
          };
          plinv = new itemsdo.ItemsFilterView(ido);
          plinv.render();
          eb = function(err) {
            var d, _l, _len3, _results;
            _results = [];
            for (_l = 0, _len3 = theitems.length; _l < _len3; _l++) {
              d = theitems[_l];
              _results.push(format_item(plinv.itemviews[d.basic.fqin].$('.searchresultl'), d));
            }
            return _results;
          };
          cb = function(data) {
            var d, docnames, thedocs, _l, _len3, _len4, _m, _ref4, _ref5, _results;
            thedocs = {};
            _ref4 = data.response.docs;
            for (_l = 0, _len3 = _ref4.length; _l < _len3; _l++) {
              d = _ref4[_l];
              thedocs[d.bibcode] = d;
            }
            docnames = (function() {
              var _len4, _m, _ref5, _results;
              _ref5 = data.response.docs;
              _results = [];
              for (_m = 0, _len4 = _ref5.length; _m < _len4; _m++) {
                d = _ref5[_m];
                _results.push(d.bibcode);
              }
              return _results;
            })();
            _results = [];
            for (_m = 0, _len4 = theitems.length; _m < _len4; _m++) {
              d = theitems[_m];
              if (_ref5 = d.basic.name, __indexOf.call(docnames, _ref5) >= 0) {
                e = thedocs[d.basic.name];
              } else {
                e = {};
              }
              plinv.itemviews[d.basic.fqin].e = e;
              _results.push(format_item(plinv.itemviews[d.basic.fqin].$('.searchresultl'), e));
            }
            return _results;
          };
          return syncs.send_bibcodes(config.bq1url, theitems, cb, eb);
        });
      });
    });
    loc = config.loc;
    nonqloc = loc.href.split('?')[0];
    if (sections.$ua.attr('data') === 'off') {
      if (nonqloc === loc.href) {
        urla = loc + "?userthere=true";
      } else {
        urla = loc + "&userthere=true";
      }
      sections.$ua.attr('href', urla);
      sections.$ua.attr('data', 'on');
    }
    sortdict = flip_sorter(config.querystring);
    $('#sortby').text(sortdict.ftext);
    $('#sortasc').html(sortdict.atext);
    $('#sortednow').attr("class", "text-info pull-right").text("Sorted by " + sortdict.fnowtext + ", " + sortdict.anowtext + ".");
    $('#sortasc').click(function(e) {
      e.preventDefault();
      return window.location = nonqloc + "?" + sortdict.oqs + "&" + 'sort=' + sortdict.fnow + ':' + sortdict.aout;
    });
    return $('#sortby').click(function(e) {
      e.preventDefault();
      return window.location = nonqloc + "?" + sortdict.oqs + "&" + 'sort=' + sortdict.fout + ':' + sortdict.anow;
    });
  };

  root.postablefilter = {
    do_postable_info: do_postable_info,
    do_postable_filter: do_postable_filter,
    do_tags: do_tags
  };

}).call(this);
