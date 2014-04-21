(function(window) {
  "use strict";
  var CanvasPrototype = window.HTMLCanvasElement && window.HTMLCanvasElement.prototype, hasBlobConstructor = window.Blob && function() {
    try {
      return Boolean(new Blob());
    } catch (e) {
      return false;
    }
  }(), hasArrayBufferViewSupport = hasBlobConstructor && window.Uint8Array && function() {
    try {
      return new Blob([ new Uint8Array(100) ]).size === 100;
    } catch (e) {
      return false;
    }
  }(), BlobBuilder = window.BlobBuilder || window.WebKitBlobBuilder || window.MozBlobBuilder || window.MSBlobBuilder, dataURLtoBlob = (hasBlobConstructor || BlobBuilder) && window.atob && window.ArrayBuffer && window.Uint8Array && function(dataURI) {
    var byteString, arrayBuffer, intArray, i, mimeString, bb;
    if (dataURI.split(",")[0].indexOf("base64") >= 0) {
      byteString = atob(dataURI.split(",")[1]);
    } else {
      byteString = decodeURIComponent(dataURI.split(",")[1]);
    }
    arrayBuffer = new ArrayBuffer(byteString.length);
    intArray = new Uint8Array(arrayBuffer);
    for (i = 0; i < byteString.length; i += 1) {
      intArray[i] = byteString.charCodeAt(i);
    }
    mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
    if (hasBlobConstructor) {
      return new Blob([ hasArrayBufferViewSupport ? intArray : arrayBuffer ], {
        type: mimeString
      });
    }
    bb = new BlobBuilder();
    bb.append(arrayBuffer);
    return bb.getBlob(mimeString);
  };
  if (window.HTMLCanvasElement && !CanvasPrototype.toBlob) {
    if (CanvasPrototype.mozGetAsFile) {
      CanvasPrototype.toBlob = function(callback, type, quality) {
        if (quality && CanvasPrototype.toDataURL && dataURLtoBlob) {
          callback(dataURLtoBlob(this.toDataURL(type, quality)));
        } else {
          callback(this.mozGetAsFile("blob", type));
        }
      };
    } else if (CanvasPrototype.toDataURL && dataURLtoBlob) {
      CanvasPrototype.toBlob = function(callback, type, quality) {
        callback(dataURLtoBlob(this.toDataURL(type, quality)));
      };
    }
  }
  if (typeof define === "function" && define.amd) {
    define(function() {
      return dataURLtoBlob;
    });
  } else {
    window.dataURLtoBlob = dataURLtoBlob;
  }
})(this);

(function(global, undefined) {
  var G = global.G = typeof exports == "undefined" ? {} : exports;
  G.version = "0.0.9";
  var _decode_uri_component = decodeURIComponent, _encode_uri_component = encodeURIComponent, _xmlns = "http://www.w3.org/2000/xmlns/", _xmlns_svg = "http://www.w3.org/2000/svg", _xmlns_xlink = "http://www.w3.org/1999/xlink", _is_array = Array.isArray, URL = global.URL || global.webkitURL;
  var _url_parse_key = [ "href", "protocol", "origin", "userInfo", "username", "password", "hostname", "port", "relative", "pathname", "directory", "file", "search", "hash" ], _url_parse_qname = [ "searchKey", "searchList" ], _url_parse_strict = /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/, _url_parse_search = /(?:^|&)([^&=]*)=?([^&]*)/g, _url_parse = function(str) {
    var uri = {
      toString: _url_unparse,
      join: _url_join,
      update: _url_update
    }, m = _url_parse_strict.exec(str || ""), i = 14;
    while (i--) uri[_url_parse_key[i]] = m[i] || "";
    var search_key = uri[_url_parse_qname[0]] = {}, search_list = uri[_url_parse_qname[1]] = {};
    uri[_url_parse_key[12]].replace(_url_parse_search, function($0, key, val) {
      if (key) {
        key = _decode_uri_component(key);
        val = _decode_uri_component(val);
        search_key[key] = val;
        (search_list[key] = search_list[key] || []).push(val);
      }
    });
    return uri;
  }, _url_unparse = function(self) {
    self = self || this;
    var protocol = self[_url_parse_key[1]] || "http", username = self[_url_parse_key[4]], password = self[_url_parse_key[5]], hostname = self[_url_parse_key[6]], port = self[_url_parse_key[7]], pathname = self[_url_parse_key[9]], search = self[_url_parse_key[12]], hash = self[_url_parse_key[13]], search_key = self[_url_parse_qname[0]], search_list = self[_url_parse_qname[1]], parts = hostname ? [ protocol, "://" ] : [], qparts = [], key, vals, i, l;
    if (username) {
      parts.push(username);
      if (password) parts.push(":", password);
      parts.push("@");
    }
    parts.push(hostname);
    if (port) parts.push(":", port);
    parts.push(pathname || (hostname ? "/" : ""));
    if (search) {
      parts.push("?", search);
    } else {
      if (search_key) {
        for (key in search_key) {
          qparts.push(_encode_uri_component(key) + "=" + _encode_uri_component(search_key[key]));
        }
      } else if (search_list) {
        for (key in search_list) {
          for (i = 0, vals = search_list[key], l = vals.length; i < l; i++) {
            qparts.push(_encode_uri_component(key) + "=" + _encode_uri_component(vals[i]));
          }
          if (!l) qparts.push(key);
        }
      }
      if (qparts.length) parts.push("?", qparts.join("&"));
    }
    if (hash) parts.push("#", hash);
    return parts.join("");
  }, _url_join = function(urlstr, options) {
    options = options || {};
    var self = this, sources = self[_url_parse_key[9]].split("/"), ptr = sources.length - 1, url = _url_parse(urlstr), targets = url.pathname.split("/"), l = targets.length, i, frag;
    if (typeof options.query == "undefined") options.query = true;
    if (typeof options.hash == "undefined") options.hash = true;
    for (i = 0; i < 14; i++) {
      if (i == 9) {
        continue;
      }
      if (i == 12 && !options.query) {
        continue;
      }
      if (i == 13 && !options.hash) {
        continue;
      }
      if (url[_url_parse_key[i]]) self[_url_parse_key[i]] = url[_url_parse_key[i]];
    }
    if (options.query && url[_url_parse_key[12]]) {
      self[_url_parse_qname[0]] = url[_url_parse_qname[0]];
      self[_url_parse_qname[1]] = url[_url_parse_qname[1]];
    }
    for (i = 0; i < l; i++) {
      frag = targets[i];
      if (frag == ".") {
        sources[ptr] = "";
      } else if (frag == "..") {
        sources[--ptr] = "";
      } else if (frag === "") {
        if (l > 1) {
          if (!i) {
            sources[0] = frag;
            ptr = 1;
          }
          if (i == l - 1) sources[ptr] = frag;
        }
      } else {
        sources[ptr] = frag;
        if (i < l - 1) ptr++;
      }
    }
    var path = self[_url_parse_key[9]] = sources.slice(0, ptr + 1).join("/"), parts = path.split(/\//), relative = [ path ];
    if (self[_url_parse_key[12]]) relative.push("?", self[_url_parse_key[12]]);
    if (self[_url_parse_key[13]]) relative.push("#", self[_url_parse_key[13]]);
    self[_url_parse_key[8]] = relative.join("");
    self[_url_parse_key[10]] = parts.slice(0, parts.length - 1).join("/") + "/";
    self[_url_parse_key[11]] = parts[parts.length - 1];
    return self;
  }, _url_update = function(args) {
    var self = this, search_key = self[_url_parse_qname[0]], search_list = self[_url_parse_qname[1]], qparts = [], key, val;
    for (key in args) {
      val = args[key];
      if (val === null) {
        delete search_key[key];
        delete search_list[key];
      } else if (_is_array(val)) {} else {
        search_key[key] = val;
        search_list[key] = [ val ];
      }
    }
    for (key in search_key) {
      qparts.push(_encode_uri_component(key) + "=" + _encode_uri_component(search_key[key]));
    }
    self.search = qparts.join("&");
    return self;
  };
  G.csv = function(array, dialect) {
    dialect = dialect || {};
    var lineterminator = dialect.lineterminator || "\n", delimiter = dialect.delimiter || ",", row = 0, nrows = array.length, col, ncols, row_data, val, vals, output = [], colpos = {}, colcount = 0, quotable = new RegExp('("|' + delimiter + "|\n)", "g");
    if (!nrows) {} else if (_is_array(array[0])) {
      for (;row < nrows; row++) {
        row_data = array[row];
        ncols = row_data.length;
        for (col = 0; col < ncols; col++) {
          val = String(row_data[col]).replace(/"/g, '""');
          if (val.search(quotable) >= 0) val = '"' + val + '"';
          if (col > 0) val = delimiter + val;
          output.push(val);
        }
        output.push(lineterminator);
      }
    } else {
      for (;row < nrows; row++) {
        row_data = array[row];
        vals = [];
        for (col in row_data) {
          val = String(row_data[col]).replace(/"/g, '""');
          if (val.search(quotable) >= 0) val = '"' + val + '"';
          if (!(col in colpos)) colpos[col] = colcount++;
          vals[colpos[col]] = val;
        }
        output.push(vals.join(delimiter));
        output.push(lineterminator);
      }
      vals = [];
      for (col in colpos) {
        val = String(col).replace(/"/g, '""');
        if (val.search(quotable) >= 0) val = '"' + val + '"';
        vals.push(val);
      }
      output.unshift(lineterminator);
      output.unshift(vals.join(delimiter));
    }
    return output.join("");
  };
  function getStyle(sheet, output) {
    var i = -1, rule, nrules;
    if (!sheet.cssRules) return;
    nrules = sheet.cssRules.length;
    while (++i < nrules) {
      rule = sheet.cssRules[i];
      if (rule.type == 3) getStyle(rule.styleSheet, output); else if (rule.selectorText && rule.selectorText.indexOf(">") == -1) output.push(rule.cssText);
    }
  }
  function download_blob(blob, options) {
    var nav = global.navigator, url, $a;
    if (nav.msSaveOrOpenBlob && nav.msSaveOrOpenBlob.bind(nav)) return nav.msSaveOrOpenBlob(blob, options.file);
    url = URL.createObjectURL(blob);
    $a = $("<a></a>").attr("download", options.file).attr("href", url).css("display", "none").appendTo("body").dispatch("click");
    setTimeout(function() {
      $a.remove();
      URL.revokeObjectURL(url);
    }, 10);
  }
  function svgize(node) {
    if (!node.hasAttributeNS(_xmlns, "xmlns")) node.setAttributeNS(_xmlns, "xmlns", _xmlns_svg);
    if (!node.hasAttributeNS(_xmlns, "xmlns:xlink")) node.setAttributeNS(_xmlns, "xmlns:xlink", _xmlns_xlink);
    return node;
  }
  G.download = function(options) {
    var mime = options.mime, source = options.source, i = -1, sheets, nsheets, style, img, blob, node, url, bounds, canvas, ctx;
    if (options.svg) {
      mime = mime || "application/svg;charset=utf-8";
      node = svgize($(options.svg).get(0));
      if (!source) {
        source = new XMLSerializer().serializeToString(node);
        if (!options.nostyle) {
          sheets = global.document.styleSheets || [];
          style = [];
          nsheets = sheets.length;
          i = -1;
          while (++i < nsheets) if (sheets[i]) getStyle(sheets[i], style);
          if (style.length) source = source.replace(/>/, "><defs><style><![CDATA[" + style.join("\n") + "]]></style></defs>");
        }
        source = '<?xml version="1.0" standalone="no"?>' + source;
      }
      download_blob(new Blob([ source ], {
        type: mime
      }), options);
    } else if (options.png) {
      mime = mime || "image/png";
      node = svgize($(options.png).get(0));
      img = new Image();
      source = new XMLSerializer().serializeToString(node);
      blob = new Blob([ source ], {
        type: "image/svg+xml;charset=utf-8"
      });
      url = URL.createObjectURL(blob);
      img.onload = function() {
        bounds = node.getBoundingClientRect();
        canvas = $("<canvas></canvas>").attr("width", options.width || bounds.width).attr("height", options.height || bounds.height).appendTo("body").css("display", "none").get(0);
        ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        canvas.toBlob(function(blob) {
          download_blob(blob, options);
          setTimeout(function() {
            $(canvas).remove();
            URL.revokeObjectURL(url);
          }, 10);
        }, mime);
      };
      img.src = url;
    } else if (options.csv) {
      mime = mime || "text/csv;charset-utf-8";
      source = G.csv(options.csv);
      download_blob(new Blob([ source ], {
        type: mime
      }), options);
    } else {
      mime = mime || "text/html;charset-utf-8";
      download_blob(new Blob([ options.source ], {
        type: mime
      }), options);
    }
  };
  G.zoom = function(options) {
    options = options || {};
    var selector = options.selector, speed = options.speed || 50, container = d3.select(selector), children = d3.selectAll(container.node().children), abruptzoom = d3.behavior.zoom().on("zoom", function() {
      children.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
      smoothzoom.translate(d3.event.translate).scale(d3.event.scale);
    }), smoothzoom = d3.behavior.zoom().on("zoom", function() {
      children.transition(speed).attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
      abruptzoom.translate(d3.event.translate).scale(d3.event.scale);
    });
    if (options.off) {
      container.on(".zoom", null);
      children.classed("zoom", true).transition().attr("transform", "");
    } else {
      container.call(abruptzoom).classed("zoom", false);
    }
    return {
      to: function(nodes) {
        var bounds = {}, i = 0, el, box, trans, scale;
        if (!nodes || !nodes.length) {
          return smoothzoom.translate([ 0, 0 ]).scale(1).event(container);
        }
        for (;el = nodes[i]; i++) {
          box = el.getBBox(), trans = (el.getAttribute("transform") || "").match(/translate\(([\+\-\d\.]+),([\+\-\d\.]+)\)/);
          if (trans) {
            box.x += +trans[1];
            box.y += +trans[2];
          }
          if (!(box.x >= bounds.x)) bounds.x = box.x;
          if (!(box.y >= bounds.y)) bounds.y = box.y;
          if (!(box.x + box.width <= bounds.x2)) bounds.x2 = box.x + box.width;
          if (!(box.y + box.height <= bounds.y2)) bounds.y2 = box.y + box.height;
        }
        bounds.width = bounds.x2 - bounds.x;
        bounds.height = bounds.y2 - bounds.y;
        scale = Math.min(width / bounds.width, height / bounds.height) * .7;
        smoothzoom.translate([ (-bounds.x - bounds.width / 2) * scale + width / 2, (-bounds.y - bounds.height / 2) * scale + height / 2 ]).scale(scale).event(container);
      }
    };
  };
  var $ = global.jQuery, jQuery = $, findall = function(node, selector) {
    return node.filter(selector).add(node.find(selector));
  }, notall = function(node, selector) {
    return node.not(selector).add(node.not(selector));
  };
  getSize = function(node) {
    var $node = $(node), old_display = $node.css("display"), result = {};
    if (old_display != "block") $node.css("display", "block");
    result.width = $node.width();
    result.height = $node.height();
    if (old_display != "block") $node.css("display", old_display);
    return result;
  };
  if ($) {
    var rclass = /[\t\r\n\f]/g, core_rnotwhite = /\S+/g;
    $.fn.addClass = function(value) {
      var classes, elem, cur, clazz, j, hasBaseVal, cls, i = 0, len = this.length, proceed = typeof value === "string" && value;
      if (jQuery.isFunction(value)) {
        return this.each(function(j) {
          jQuery(this).addClass(value.call(this, j, typeof this.className == "object" ? this.className.baseVal : this.className));
        });
      }
      if (proceed) {
        classes = (value || "").match(core_rnotwhite) || [];
        for (;i < len; i++) {
          elem = this[i];
          hasBaseVal = typeof elem.className == "object";
          cls = hasBaseVal ? elem.className.baseVal : elem.className;
          cur = elem.nodeType === 1 && (cls ? (" " + cls + " ").replace(rclass, " ") : " ");
          if (cur) {
            j = 0;
            while (clazz = classes[j++]) {
              if (cur.indexOf(" " + clazz + " ") < 0) {
                cur += clazz + " ";
              }
            }
            if (hasBaseVal) {
              elem.className.baseVal = jQuery.trim(cur);
            } else {
              elem.className = jQuery.trim(cur);
            }
          }
        }
      }
      return this;
    };
    $.fn.removeClass = function(value) {
      var classes, elem, cur, clazz, j, hasBaseVal, cls, i = 0, len = this.length, proceed = arguments.length === 0 || typeof value === "string" && value;
      if (jQuery.isFunction(value)) {
        return this.each(function(j) {
          jQuery(this).removeClass(value.call(this, j, typeof this.className == "object" ? this.className.baseVal : this.className));
        });
      }
      if (proceed) {
        classes = (value || "").match(core_rnotwhite) || [];
        for (;i < len; i++) {
          elem = this[i];
          hasBaseVal = typeof elem.className == "object";
          cls = hasBaseVal ? elem.className.baseVal : elem.className;
          cur = elem.nodeType === 1 && (cls ? (" " + cls + " ").replace(rclass, " ") : "");
          if (cur) {
            j = 0;
            while (clazz = classes[j++]) {
              while (cur.indexOf(" " + clazz + " ") >= 0) {
                cur = cur.replace(" " + clazz + " ", " ");
              }
            }
            if (hasBaseVal) {
              elem.className.baseVal = value ? jQuery.trim(cur) : "";
            } else {
              elem.className = value ? jQuery.trim(cur) : "";
            }
          }
        }
      }
      return this;
    };
    $.fn.toggleClass = function(value, stateVal) {
      var type = typeof value;
      if (typeof stateVal === "boolean" && type === "string") {
        return stateVal ? this.addClass(value) : this.removeClass(value);
      }
      if (jQuery.isFunction(value)) {
        return this.each(function(i) {
          jQuery(this).toggleClass(value.call(this, i, typeof this.className == "object" ? this.className.baseVal : this.className, stateVal), stateVal);
        });
      }
      return this.each(function() {
        var hasBaseVal, cls;
        if (type === "string") {
          var className, i = 0, self = jQuery(this), classNames = value.match(core_rnotwhite) || [];
          while (className = classNames[i++]) {
            if (self.hasClass(className)) {
              self.removeClass(className);
            } else {
              self.addClass(className);
            }
          }
        } else if (type === core_strundefined || type === "boolean") {
          hasBaseVal = typeof this.className == "object";
          cls = hasBaseVal ? this.className.baseVal : this.className;
          if (cls) {
            data_priv.set(this, "__className__", cls);
          }
          if (hasBaseVal) {
            this.className.baseVal = this.className.baseVal || value === false ? "" : data_priv.get(this, "__className__") || "";
          } else {
            this.className = this.className || value === false ? "" : data_priv.get(this, "__className__") || "";
          }
        }
      });
    };
    $.fn.hasClass = function(selector) {
      var className = " " + selector + " ", cls, i = 0, l = this.length;
      for (;i < l; i++) {
        cls = this[i].className;
        if (this[i].nodeType === 1 && (" " + (typeof cls == "object" ? cls.baseVal : cls) + " ").replace(rclass, " ").indexOf(className) >= 0) {
          return true;
        }
      }
      return false;
    };
    $.fn.aspect = function(options) {
      options = options || {};
      var resize, self = this, width = options.width, height = options.height, doc = self[0].ownerDocument, $win = $(doc.defaultView || doc.parentWindow);
      if (options.off) {
        $win.off(".g.aspect");
        return self;
      }
      resize = function() {
        (options.selector ? findall(self, options.selector) : self).each(function() {
          var $this = $(this), w = $this.data("width") || width, h = $this.data("height") || height, box = getSize(this);
          if (h) $this.css("height", Math.ceil(h * box.width)); else if (w) $this.css("width", Math.ceil(w * box.height));
        });
      };
      $win.on("resize.g.aspect", resize).on("orientationchange.g.aspect", resize);
      resize();
      return self;
    };
    var _event;
    try {
      new Event("click");
      _event = function(name, options) {
        if (name.match(/click$|^mouse|^menu$/)) return new MouseEvent(name, options); else if (name.match(/^key/)) return new KeyboardEvent(name, options); else if (name.match(/^focus|^blur$/)) return new FocusEvent(name, options); else return new Event(name, options);
      };
    } catch (e) {
      _event = function(name, options) {
        var evt = document.createEvent("event");
        evt.initEvent(name, options.bubbles, options.cancelable);
        return evt;
      };
    }
    $.fn.dispatch = function(name, options) {
      return this.each(function() {
        this.dispatchEvent(_event(name, $.extend({
          bubbles: true,
          cancelable: true
        }, options)));
      });
    };
    $.fn.urlfilter = function(options) {
      options = options || {};
      var self = this, attr = options.attr || "href", selector = options.selector || "[" + attr + "]", remove = "remove" in options ? options.remove : true, doc = self[0].ownerDocument, loc = (doc.defaultView || doc.parentWindow).location, default_target = options.target;
      if (options.off) return self.off("click.urlfilter");
      return self.on("click.urlfilter", selector, function(e) {
        e.preventDefault();
        var $this = $(this), target = $this.data("target") || default_target, href = $this.attr(attr), q = G.url.parse(href)[_url_parse_qname[0]], $target, url, key;
        if (remove) for (key in q) if (q[key] === "") q[key] = null;
        if (!target) url = loc.href; else if (target == "#") url = loc.hash.replace(/^#/, ""); else {
          $target = $(target);
          url = $target.data("src");
        }
        url = G.url.parse(url).join(href, {
          query: false,
          hash: false
        }).update(q);
        if (!target) loc.href = url; else if (target == "#") loc.hash = url; else $target.data("src", url).load(url.toString());
      });
    };
    $.fn.highlight = function(options) {
      options = options || {};
      var self = this, attr = options.attr || "data-highlight", selector = options.selector || "[" + attr + "]", leaveDelay = options.leaveDelay || 30, toggle = options.toggle, exit_timer, selected = [];
      if (options.off) return self.off(".g.highlight");
      function select(selected, source) {
        var $source = $(source), $target = $($source.data("target") || options.target || selector), hideClass = $source.data("hide-class") || options.hideClass || "fade", showClass = $source.data("show-class") || options.showClass || "", highlighted = $(), unhighlighted, nselected = selected.length, i = nselected;
        if (nselected) {
          while (i--) highlighted = highlighted.add(findall($target, $(selected[i]).attr(attr)));
          unhighlighted = $target.not(highlighted);
          if (showClass) {
            notall(highlighted, "." + showClass).addClass(showClass);
            findall(unhighlighted, "." + showClass).removeClass(showClass);
          }
          if (hideClass) {
            findall(highlighted, "." + hideClass).removeClass(hideClass);
            notall(unhighlighted, "." + hideClass).addClass(hideClass);
          }
        } else {
          if (showClass) findall($target, "." + showClass).removeClass(showClass);
          if (hideClass) findall($target, "." + hideClass).removeClass(hideClass);
        }
        self.trigger({
          type: "shown.g.highlight",
          selected: $(selected),
          matches: (nselected ? highlighted : $target).length
        });
        console.log(selected,source);
      }
      self.on("mouseenter.g.highlight", selector, function(e) {
        if (exit_timer) exit_timer = clearTimeout(exit_timer);
        if (!selected.length) select([ e.target ], this);
      }).on("mouseleave.g.highlight", selector, function(e) {
        if (exit_timer) exit_timer = clearTimeout(exit_timer);
        var source = this;
        if (!selected.length) exit_timer = setTimeout(function() {
          select([], source);
        }, leaveDelay);
      }).on("click.g.highlight", selector, function(e) {
        var $this = $(this), index;
        if ($this.data("toggle") || toggle) {
          index = selected.indexOf(e.target);
          if (index >= 0) {
            selected.splice(index, 1);
            $this.removeClass("active");
          } else {
            selected.push(e.target);
            $this.addClass("active");
          }
          select(selected, this);
        }
      });
      return self;
    };
    $.fn.panzoom = function(options) {
      options = options || {};
      var self = this, attr = options.attr || "data-zoom", selector = options.selector || "[" + attr + "]", default_target = options.target, default_zoom = options.zoom || 4, viewBox = "viewBox", animdata = "animated";
      if (options.off) return self.off("click.panzoom");
      self.on("click", selector, function(e) {
        var $selector = $(this), target = $selector.data("target") || default_target, zoom = $selector.attr(attr) || default_zoom, $target = $(target);
        function clearZoom(e) {
          $target.each(function() {
            var newbox = $(this).data(viewBox);
            if (global.d3) d3.select(this).transition().duration(100).attr(viewBox, newbox); else this.setAttribute(viewBox, newbox);
          });
        }
        function setZoom(e) {
          $target.each(function() {
            var $this = $(this), viewBoxParts = $this.data(viewBox), size = this.getBoundingClientRect(), width = +viewBoxParts[2] || size.width, height = +viewBoxParts[3] || size.height, offset = $this.offset(), x = e.pageX - offset.left, y = e.pageY - offset.top, newbox = [ x, y, width / zoom, height / zoom ].join(" ");
            if (global.d3 && !e.type.match(/move/)) {
              $this.data(animdata, true);
              d3.select(this).transition().duration(100).attr(viewBox, newbox).each("end", function() {
                $this.data(animdata, false);
              });
            } else if (!$this.data(animdata)) this.setAttribute(viewBox, newbox);
          });
        }
        if ($selector.is(".active")) {
          clearZoom();
          $target.off(".panzoom").each(function() {
            $(this).removeData(viewBox);
          });
        } else {
          $target.each(function() {
            $(this).data(viewBox, (this.getAttribute(viewBox) || "").split(/,|\s+/));
          }).on("mousemove.panzoom", setZoom);
          setZoom(e);
        }
        $selector.toggleClass("active");
      });
      return self;
    };
    $.fn.reveal = function(options) {
      options = options || {};
      var self = this, attr = options.attr || "data-reveal", selector = options.selector || "[" + attr + "]", done = {};
      if (options.off) return self.off(".g.reveal");
      $(selector).each(function() {
        var $source = $(this), target = $source.data("target") || options.target || selector, start, $target, type, hideClass, hidden;
        if (!done[target]) {
          start = +($source.data("start") || options.start || 0);
          hideClass = $source.data("hide-class") || options.hideClass || "fade";
          type = $source.data("type") || options.type || "overlay";
          hidden = "." + hideClass;
          $target = $(target);
          if (type == "overlay") {
            $target.eq(start).filter(hidden).removeClass(hideClass);
            $target.slice(start + 1).not(hidden).addClass(hideClass);
          } else if (type == "single") {
            $target.eq(start).filter(hidden).removeClass(hideClass);
            $target.not($target.eq(start)).not(hidden).addClass(hideClass);
          }
          done[target] = 1;
        }
      });
      return self.on("click.g.reveal", selector, function(e) {
        var $source = $(this), $target = $($source.data("target") || options.target || selector), hideClass = $source.data("hide-class") || options.hideClass || "fade", type = $source.data("type") || options.type || "overlay", loop = $source.data("loop") || options.loop, hidden = "." + hideClass, reveal = $source.attr(attr), $hidden, $shown, $current, slide, nslides;
        if (type == "overlay") {
          if (reveal.match(/next/i)) {
            $hidden = $target.filter(hidden);
            if (!$hidden.length) {
              if (loop) {
                $target.slice(1).addClass(hideClass);
                $current = $target.eq(0);
              } else {
                $current = $target.last();
              }
            } else {
              $current = $hidden.first().removeClass(hideClass);
            }
            slide = $target.index($current);
          } else if (reveal.match(/prev/i)) {
            $shown = $target.not(hidden);
            if ($shown.length <= 1) {
              if (loop) {
                $target.removeClass(hideClass);
                $current = $target.last();
              }
            } else {
              $shown.last().addClass(hideClass);
              $current = $shown.eq(-2);
            }
            slide = $target.index($current);
          } else {
            slide = +reveal;
            if (slide < 0) slide = $target.length + slide;
            $target.slice(0, slide + 1).filter(hidden).removeClass(hideClass);
            $target.slice(slide + 1).not(hidden).addClass(hideClass);
          }
        } else if (type == "single") {
          nslides = $target.length;
          $shown = $target.not(hidden);
          if (reveal.match(/next/i)) {
            if ($shown.length) {
              slide = $target.index($shown.last()) + 1;
              if (slide >= nslides) slide = loop ? 0 : nslides - 1;
            } else slide = 0;
          } else if (reveal.match(/prev/i)) {
            if ($shown.length) {
              slide = $target.index($shown.last()) - 1;
              if (slide < 0) slide = loop ? nslides - 1 : 0;
            } else slide = nslides - 1;
          } else slide = +reveal;
          $current = $target.eq(slide);
          $current.filter(hidden).removeClass(hideClass);
          $target.not($current).not(hidden).addClass(hideClass);
        }
        $source.trigger({
          type: "shown.g.reveal",
          slide: slide
        });
      });
    };
    var _G_search_transform = function(s) {
      return (s || "").toLowerCase().replace(/\s+/g, " ").replace(/^ /, "").replace(/ $/, "");
    }, _G_search_change = function(s) {
      return s.replace(/\s+/g, ".*");
    };
    $.fn.search = function(options) {
      options = options || {};
      var self = this, attr = options.attr || "data-search", selector = options.selector || "[" + attr + "]", transform = options.transform || _G_search_transform, changeSearch = options.changeSearch || _G_search_change, showClass = options.showClass || "", hideClass = options.hideClass || "", lastsearch = "search-lastsearch", mapping = "search-mapping", refresh, run_search;
      if (options.off) return self.off(".g.search");
      refresh = function(e) {
        var $el = $(e.target), list = [], textattr = options.text || $el.attr(attr), targets = $($el.data("target") || options.target || (typeof textattr == "string" ? "[" + textattr + "]" : "*"));
        targets.each(typeof textattr == "function" ? function() {
          var x = textattr(this);
          list.push([ $(this), x, transform(x), false ]);
        } : textattr == "@text" ? function() {
          var x = this.textContent;
          list.push([ $(this), x, transform(x), false ]);
        } : function() {
          var x = this.getAttribute(textattr);
          list.push([ $(this), x, transform(x), false ]);
        });
        $el.data(mapping, list);
        return list;
      };
      run_search = function(e) {
        var $el = $(e.target), original_search = $el.val(), search = changeSearch(transform(original_search)), lastsearch_value = $el.data(lastsearch);
        if (lastsearch_value == search) return;
        var map = $el.data(mapping), re = new RegExp(search), showcls = $el.data("show-class") || showClass, hidecls = $el.data("hide-class") || hideClass || (showcls ? "" : "fade"), i, cell, count;
        $el.data(lastsearch, search);
        if (!map) map = refresh(e);
        count = map.length;
        if (!search.length) {
          for (i = 0; cell = map[i]; i++) {
            if (cell[3]) {
              if (hidecls) cell[0].removeClass(hidecls);
            } else {
              if (showcls) cell[0].removeClass(showcls);
            }
            cell[3] = false;
          }
        } else {
          for (i = 0; cell = map[i]; i++) {
            var hide = !cell[2].match(re);
            if (hide !== cell[3] || !lastsearch_value) {
              if (hidecls) cell[0][hide ? "addClass" : "removeClass"](hidecls);
              if (showcls) cell[0][!hide ? "addClass" : "removeClass"](showcls);
              cell[3] = hide;
            }
            if (hide) count--;
          }
        }
        $el.trigger({
          type: "shown.g.search",
          searchText: original_search,
          search: search,
          matches: count
        });
      };
      return self.on("keyup.g.search", selector, run_search).on("change.g.search", selector, run_search).on("refresh.g.search", refresh);
    };
  }
  G.unpack = function() {
    var force, width, height;
    function self(update) {
      var nodes = update.data(), i = -1, l = nodes.length;
      while (++i < l) {
        nodes[i].x0 = nodes[i].x;
        nodes[i].y0 = nodes[i].y;
      }
      function gravity(k) {
        return function(d) {
          d.x += (d.x0 - d.x) * k;
          d.y += (d.y0 - d.y) * k;
        };
      }
      function collide(k) {
        var q = d3.geom.quadtree(nodes);
        return function(node) {
          var nr = node.r, nx1 = node.x - nr, nx2 = node.x + nr, ny1 = node.y - nr, ny2 = node.y + nr;
          q.visit(function(quad, x1, y1, x2, y2) {
            if (quad.point && quad.point !== node) {
              var x = node.x - quad.point.x, y = node.y - quad.point.y, l = x * x + y * y, r = nr + quad.point.r;
              if (l < r * r) {
                l = ((l = Math.sqrt(l)) - r) / l * k;
                node.x -= x *= l;
                node.y -= y *= l;
                quad.point.x += x;
                quad.point.y += y;
              }
            }
            return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
          });
        };
      }
      force.size([ width, height ]).nodes(nodes).on("tick", function tick(e) {
        update.each(gravity(e.alpha * .1)).each(collide(.5)).attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
        });
      }).start();
    }
    self.width = function(v) {
      if (!arguments.length) return width;
      width = v;
      return self;
    };
    self.height = function(v) {
      if (!arguments.length) return height;
      height = v;
      return self;
    };
    self.force = function(v) {
      if (!arguments.length) return force;
      force = v;
      return self;
    };
    return self.force(d3.layout.force().charge(0).gravity(.01));
  };
  G.map = function() {
    var shape, width, height, projection, path, unpack, size = function(d, i) {
      return 5;
    }, self = {};
    function center_shape() {
      projection.scale(1).translate([ 0, 0 ]);
      var b = path.bounds(shape), s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height), t = [ (width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2 ];
      projection.scale(s).translate(t);
    }
    self.map = function(selection) {
      center_shape();
      var update = selection.selectAll("path.map").data(shape.features);
      update.transition().attr("transform", null).attr("d", path);
      update.enter().append("path").attr("class", "map").attr("transform", null).attr("d", path);
      update.exit().remove();
      return update;
    };
    self.dorling = function(selection) {
      center_shape();
      var circle_path = function(d, i) {
        var r = size(d, i);
        return r > 0 ? "M0,0m-{r},0a{r},{r} 0 1,0 {d},0a{r},{r} 0 1,0 -{d},0".replace(/\{r\}/g, r).replace(/\{d\}/g, 2 * r) : "M0,0";
      }, nodes = shape.features.map(function(d, i) {
        var centroid = path.centroid(d.geometry);
        return typeof centroid === "undefined" ? {
          x: 0,
          y: 0
        } : {
          x: centroid[0],
          y: centroid[1],
          r: size(d, i),
          properties: d.properties
        };
      }), update = selection.selectAll("path.map").data(nodes);
      update.attr("d", circle_path).attr("transform", function(d, i) {
        return "scale(" + size(d, i) + ")";
      });
      update.enter().append("path").attr("class", "map").attr("transform", function(d, i) {
        return "scale(" + size(d, i) + ")";
      }).attr("d", circle_path);
      update.exit().remove();
      if (!unpack) {
        unpack = G.unpack().width(width).height(height);
      }
      unpack(update);
      return update;
    };
    self.shape = function(v) {
      if (!arguments.length) return shape;
      shape = v;
      return self;
    };
    self.width = function(v) {
      if (!arguments.length) return width;
      width = v;
      return self;
    };
    self.height = function(v) {
      if (!arguments.length) return height;
      height = v;
      return self;
    };
    self.force = function(v) {
      if (!arguments.length) return force;
      force = v;
      return self;
    };
    self.size = function(v) {
      if (!arguments.length) return size;
      size = v;
      return self;
    };
    self.path = function(v) {
      if (!arguments.length) return path;
      path = v;
      return self;
    };
    self.projection = function(v) {
      if (!arguments.length) return projection;
      projection = v;
      path = d3.geo.path().projection(v);
      return self;
    };
    return self.projection(d3.geo.mercator()).force(d3.layout.force().charge(0).gravity(.01));
  };
  G.url = {
    parse: _url_parse,
    unparse: _url_unparse
  };
})(this);