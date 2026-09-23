/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const k = globalThis, V = k.ShadowRoot && (k.ShadyCSS === void 0 || k.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, q = Symbol(), Q = /* @__PURE__ */ new WeakMap();
let lt = class {
  constructor(t, e, s) {
    if (this._$cssResult$ = !0, s !== q) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = t, this.t = e;
  }
  get styleSheet() {
    let t = this.o;
    const e = this.t;
    if (V && t === void 0) {
      const s = e !== void 0 && e.length === 1;
      s && (t = Q.get(e)), t === void 0 && ((this.o = t = new CSSStyleSheet()).replaceSync(this.cssText), s && Q.set(e, t));
    }
    return t;
  }
  toString() {
    return this.cssText;
  }
};
const ft = (r) => new lt(typeof r == "string" ? r : r + "", void 0, q), $t = (r, ...t) => {
  const e = r.length === 1 ? r[0] : t.reduce((s, i, o) => s + ((n) => {
    if (n._$cssResult$ === !0) return n.cssText;
    if (typeof n == "number") return n;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + n + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(i) + r[o + 1], r[0]);
  return new lt(e, r, q);
}, _t = (r, t) => {
  if (V) r.adoptedStyleSheets = t.map((e) => e instanceof CSSStyleSheet ? e : e.styleSheet);
  else for (const e of t) {
    const s = document.createElement("style"), i = k.litNonce;
    i !== void 0 && s.setAttribute("nonce", i), s.textContent = e.cssText, r.appendChild(s);
  }
}, X = V ? (r) => r : (r) => r instanceof CSSStyleSheet ? ((t) => {
  let e = "";
  for (const s of t.cssRules) e += s.cssText;
  return ft(e);
})(r) : r;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const { is: mt, defineProperty: gt, getOwnPropertyDescriptor: vt, getOwnPropertyNames: yt, getOwnPropertySymbols: At, getPrototypeOf: bt } = Object, _ = globalThis, Y = _.trustedTypes, Et = Y ? Y.emptyScript : "", D = _.reactiveElementPolyfillSupport, C = (r, t) => r, L = { toAttribute(r, t) {
  switch (t) {
    case Boolean:
      r = r ? Et : null;
      break;
    case Object:
    case Array:
      r = r == null ? r : JSON.stringify(r);
  }
  return r;
}, fromAttribute(r, t) {
  let e = r;
  switch (t) {
    case Boolean:
      e = r !== null;
      break;
    case Number:
      e = r === null ? null : Number(r);
      break;
    case Object:
    case Array:
      try {
        e = JSON.parse(r);
      } catch {
        e = null;
      }
  }
  return e;
} }, F = (r, t) => !mt(r, t), tt = { attribute: !0, type: String, converter: L, reflect: !1, useDefault: !1, hasChanged: F };
Symbol.metadata ?? (Symbol.metadata = Symbol("metadata")), _.litPropertyMetadata ?? (_.litPropertyMetadata = /* @__PURE__ */ new WeakMap());
let E = class extends HTMLElement {
  static addInitializer(t) {
    this._$Ei(), (this.l ?? (this.l = [])).push(t);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(t, e = tt) {
    if (e.state && (e.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(t) && ((e = Object.create(e)).wrapped = !0), this.elementProperties.set(t, e), !e.noAccessor) {
      const s = Symbol(), i = this.getPropertyDescriptor(t, s, e);
      i !== void 0 && gt(this.prototype, t, i);
    }
  }
  static getPropertyDescriptor(t, e, s) {
    const { get: i, set: o } = vt(this.prototype, t) ?? { get() {
      return this[e];
    }, set(n) {
      this[e] = n;
    } };
    return { get: i, set(n) {
      const a = i == null ? void 0 : i.call(this);
      o == null || o.call(this, n), this.requestUpdate(t, a, s);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(t) {
    return this.elementProperties.get(t) ?? tt;
  }
  static _$Ei() {
    if (this.hasOwnProperty(C("elementProperties"))) return;
    const t = bt(this);
    t.finalize(), t.l !== void 0 && (this.l = [...t.l]), this.elementProperties = new Map(t.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(C("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(C("properties"))) {
      const e = this.properties, s = [...yt(e), ...At(e)];
      for (const i of s) this.createProperty(i, e[i]);
    }
    const t = this[Symbol.metadata];
    if (t !== null) {
      const e = litPropertyMetadata.get(t);
      if (e !== void 0) for (const [s, i] of e) this.elementProperties.set(s, i);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [e, s] of this.elementProperties) {
      const i = this._$Eu(e, s);
      i !== void 0 && this._$Eh.set(i, e);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(t) {
    const e = [];
    if (Array.isArray(t)) {
      const s = new Set(t.flat(1 / 0).reverse());
      for (const i of s) e.unshift(X(i));
    } else t !== void 0 && e.push(X(t));
    return e;
  }
  static _$Eu(t, e) {
    const s = e.attribute;
    return s === !1 ? void 0 : typeof s == "string" ? s : typeof t == "string" ? t.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    var t;
    this._$ES = new Promise((e) => this.enableUpdating = e), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), (t = this.constructor.l) == null || t.forEach((e) => e(this));
  }
  addController(t) {
    var e;
    (this._$EO ?? (this._$EO = /* @__PURE__ */ new Set())).add(t), this.renderRoot !== void 0 && this.isConnected && ((e = t.hostConnected) == null || e.call(t));
  }
  removeController(t) {
    var e;
    (e = this._$EO) == null || e.delete(t);
  }
  _$E_() {
    const t = /* @__PURE__ */ new Map(), e = this.constructor.elementProperties;
    for (const s of e.keys()) this.hasOwnProperty(s) && (t.set(s, this[s]), delete this[s]);
    t.size > 0 && (this._$Ep = t);
  }
  createRenderRoot() {
    const t = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return _t(t, this.constructor.elementStyles), t;
  }
  connectedCallback() {
    var t;
    this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (t = this._$EO) == null || t.forEach((e) => {
      var s;
      return (s = e.hostConnected) == null ? void 0 : s.call(e);
    });
  }
  enableUpdating(t) {
  }
  disconnectedCallback() {
    var t;
    (t = this._$EO) == null || t.forEach((e) => {
      var s;
      return (s = e.hostDisconnected) == null ? void 0 : s.call(e);
    });
  }
  attributeChangedCallback(t, e, s) {
    this._$AK(t, s);
  }
  _$ET(t, e) {
    var o;
    const s = this.constructor.elementProperties.get(t), i = this.constructor._$Eu(t, s);
    if (i !== void 0 && s.reflect === !0) {
      const n = (((o = s.converter) == null ? void 0 : o.toAttribute) !== void 0 ? s.converter : L).toAttribute(e, s.type);
      this._$Em = t, n == null ? this.removeAttribute(i) : this.setAttribute(i, n), this._$Em = null;
    }
  }
  _$AK(t, e) {
    var o, n;
    const s = this.constructor, i = s._$Eh.get(t);
    if (i !== void 0 && this._$Em !== i) {
      const a = s.getPropertyOptions(i), h = typeof a.converter == "function" ? { fromAttribute: a.converter } : ((o = a.converter) == null ? void 0 : o.fromAttribute) !== void 0 ? a.converter : L;
      this._$Em = i;
      const l = h.fromAttribute(e, a.type);
      this[i] = l ?? ((n = this._$Ej) == null ? void 0 : n.get(i)) ?? l, this._$Em = null;
    }
  }
  requestUpdate(t, e, s, i = !1, o) {
    var n;
    if (t !== void 0) {
      const a = this.constructor;
      if (i === !1 && (o = this[t]), s ?? (s = a.getPropertyOptions(t)), !((s.hasChanged ?? F)(o, e) || s.useDefault && s.reflect && o === ((n = this._$Ej) == null ? void 0 : n.get(t)) && !this.hasAttribute(a._$Eu(t, s)))) return;
      this.C(t, e, s);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(t, e, { useDefault: s, reflect: i, wrapped: o }, n) {
    s && !(this._$Ej ?? (this._$Ej = /* @__PURE__ */ new Map())).has(t) && (this._$Ej.set(t, n ?? e ?? this[t]), o !== !0 || n !== void 0) || (this._$AL.has(t) || (this.hasUpdated || s || (e = void 0), this._$AL.set(t, e)), i === !0 && this._$Em !== t && (this._$Eq ?? (this._$Eq = /* @__PURE__ */ new Set())).add(t));
  }
  async _$EP() {
    this.isUpdatePending = !0;
    try {
      await this._$ES;
    } catch (e) {
      Promise.reject(e);
    }
    const t = this.scheduleUpdate();
    return t != null && await t, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    var s;
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this._$Ep) {
        for (const [o, n] of this._$Ep) this[o] = n;
        this._$Ep = void 0;
      }
      const i = this.constructor.elementProperties;
      if (i.size > 0) for (const [o, n] of i) {
        const { wrapped: a } = n, h = this[o];
        a !== !0 || this._$AL.has(o) || h === void 0 || this.C(o, void 0, n, h);
      }
    }
    let t = !1;
    const e = this._$AL;
    try {
      t = this.shouldUpdate(e), t ? (this.willUpdate(e), (s = this._$EO) == null || s.forEach((i) => {
        var o;
        return (o = i.hostUpdate) == null ? void 0 : o.call(i);
      }), this.update(e)) : this._$EM();
    } catch (i) {
      throw t = !1, this._$EM(), i;
    }
    t && this._$AE(e);
  }
  willUpdate(t) {
  }
  _$AE(t) {
    var e;
    (e = this._$EO) == null || e.forEach((s) => {
      var i;
      return (i = s.hostUpdated) == null ? void 0 : i.call(s);
    }), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(t)), this.updated(t);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(t) {
    return !0;
  }
  update(t) {
    this._$Eq && (this._$Eq = this._$Eq.forEach((e) => this._$ET(e, this[e]))), this._$EM();
  }
  updated(t) {
  }
  firstUpdated(t) {
  }
};
E.elementStyles = [], E.shadowRootOptions = { mode: "open" }, E[C("elementProperties")] = /* @__PURE__ */ new Map(), E[C("finalized")] = /* @__PURE__ */ new Map(), D == null || D({ ReactiveElement: E }), (_.reactiveElementVersions ?? (_.reactiveElementVersions = [])).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const P = globalThis, et = (r) => r, z = P.trustedTypes, st = z ? z.createPolicy("lit-html", { createHTML: (r) => r }) : void 0, dt = "$lit$", $ = `lit$${Math.random().toFixed(9).slice(2)}$`, ct = "?" + $, wt = `<${ct}>`, b = document, O = () => b.createComment(""), R = (r) => r === null || typeof r != "object" && typeof r != "function", G = Array.isArray, St = (r) => G(r) || typeof (r == null ? void 0 : r[Symbol.iterator]) == "function", I = `[ 	
\f\r]`, x = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, it = /-->/g, rt = />/g, g = RegExp(`>|${I}(?:([^\\s"'>=/]+)(${I}*=${I}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), ot = /'/g, nt = /"/g, pt = /^(?:script|style|textarea|title)$/i, xt = (r) => (t, ...e) => ({ _$litType$: r, strings: t, values: e }), v = xt(1), w = Symbol.for("lit-noChange"), p = Symbol.for("lit-nothing"), at = /* @__PURE__ */ new WeakMap(), y = b.createTreeWalker(b, 129);
function ut(r, t) {
  if (!G(r) || !r.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return st !== void 0 ? st.createHTML(t) : t;
}
const Ct = (r, t) => {
  const e = r.length - 1, s = [];
  let i, o = t === 2 ? "<svg>" : t === 3 ? "<math>" : "", n = x;
  for (let a = 0; a < e; a++) {
    const h = r[a];
    let l, c, d = -1, u = 0;
    for (; u < h.length && (n.lastIndex = u, c = n.exec(h), c !== null); ) u = n.lastIndex, n === x ? c[1] === "!--" ? n = it : c[1] !== void 0 ? n = rt : c[2] !== void 0 ? (pt.test(c[2]) && (i = RegExp("</" + c[2], "g")), n = g) : c[3] !== void 0 && (n = g) : n === g ? c[0] === ">" ? (n = i ?? x, d = -1) : c[1] === void 0 ? d = -2 : (d = n.lastIndex - c[2].length, l = c[1], n = c[3] === void 0 ? g : c[3] === '"' ? nt : ot) : n === nt || n === ot ? n = g : n === it || n === rt ? n = x : (n = g, i = void 0);
    const f = n === g && r[a + 1].startsWith("/>") ? " " : "";
    o += n === x ? h + wt : d >= 0 ? (s.push(l), h.slice(0, d) + dt + h.slice(d) + $ + f) : h + $ + (d === -2 ? a : f);
  }
  return [ut(r, o + (r[e] || "<?>") + (t === 2 ? "</svg>" : t === 3 ? "</math>" : "")), s];
};
class M {
  constructor({ strings: t, _$litType$: e }, s) {
    let i;
    this.parts = [];
    let o = 0, n = 0;
    const a = t.length - 1, h = this.parts, [l, c] = Ct(t, e);
    if (this.el = M.createElement(l, s), y.currentNode = this.el.content, e === 2 || e === 3) {
      const d = this.el.content.firstChild;
      d.replaceWith(...d.childNodes);
    }
    for (; (i = y.nextNode()) !== null && h.length < a; ) {
      if (i.nodeType === 1) {
        if (i.hasAttributes()) for (const d of i.getAttributeNames()) if (d.endsWith(dt)) {
          const u = c[n++], f = i.getAttribute(d).split($), T = /([.?@])?(.*)/.exec(u);
          h.push({ type: 1, index: o, name: T[2], strings: f, ctor: T[1] === "." ? Ut : T[1] === "?" ? Ot : T[1] === "@" ? Rt : j }), i.removeAttribute(d);
        } else d.startsWith($) && (h.push({ type: 6, index: o }), i.removeAttribute(d));
        if (pt.test(i.tagName)) {
          const d = i.textContent.split($), u = d.length - 1;
          if (u > 0) {
            i.textContent = z ? z.emptyScript : "";
            for (let f = 0; f < u; f++) i.append(d[f], O()), y.nextNode(), h.push({ type: 2, index: ++o });
            i.append(d[u], O());
          }
        }
      } else if (i.nodeType === 8) if (i.data === ct) h.push({ type: 2, index: o });
      else {
        let d = -1;
        for (; (d = i.data.indexOf($, d + 1)) !== -1; ) h.push({ type: 7, index: o }), d += $.length - 1;
      }
      o++;
    }
  }
  static createElement(t, e) {
    const s = b.createElement("template");
    return s.innerHTML = t, s;
  }
}
function S(r, t, e = r, s) {
  var n, a;
  if (t === w) return t;
  let i = s !== void 0 ? (n = e._$Co) == null ? void 0 : n[s] : e._$Cl;
  const o = R(t) ? void 0 : t._$litDirective$;
  return (i == null ? void 0 : i.constructor) !== o && ((a = i == null ? void 0 : i._$AO) == null || a.call(i, !1), o === void 0 ? i = void 0 : (i = new o(r), i._$AT(r, e, s)), s !== void 0 ? (e._$Co ?? (e._$Co = []))[s] = i : e._$Cl = i), i !== void 0 && (t = S(r, i._$AS(r, t.values), i, s)), t;
}
class Pt {
  constructor(t, e) {
    this._$AV = [], this._$AN = void 0, this._$AD = t, this._$AM = e;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(t) {
    const { el: { content: e }, parts: s } = this._$AD, i = ((t == null ? void 0 : t.creationScope) ?? b).importNode(e, !0);
    y.currentNode = i;
    let o = y.nextNode(), n = 0, a = 0, h = s[0];
    for (; h !== void 0; ) {
      if (n === h.index) {
        let l;
        h.type === 2 ? l = new H(o, o.nextSibling, this, t) : h.type === 1 ? l = new h.ctor(o, h.name, h.strings, this, t) : h.type === 6 && (l = new Mt(o, this, t)), this._$AV.push(l), h = s[++a];
      }
      n !== (h == null ? void 0 : h.index) && (o = y.nextNode(), n++);
    }
    return y.currentNode = b, i;
  }
  p(t) {
    let e = 0;
    for (const s of this._$AV) s !== void 0 && (s.strings !== void 0 ? (s._$AI(t, s, e), e += s.strings.length - 2) : s._$AI(t[e])), e++;
  }
}
class H {
  get _$AU() {
    var t;
    return ((t = this._$AM) == null ? void 0 : t._$AU) ?? this._$Cv;
  }
  constructor(t, e, s, i) {
    this.type = 2, this._$AH = p, this._$AN = void 0, this._$AA = t, this._$AB = e, this._$AM = s, this.options = i, this._$Cv = (i == null ? void 0 : i.isConnected) ?? !0;
  }
  get parentNode() {
    let t = this._$AA.parentNode;
    const e = this._$AM;
    return e !== void 0 && (t == null ? void 0 : t.nodeType) === 11 && (t = e.parentNode), t;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(t, e = this) {
    t = S(this, t, e), R(t) ? t === p || t == null || t === "" ? (this._$AH !== p && this._$AR(), this._$AH = p) : t !== this._$AH && t !== w && this._(t) : t._$litType$ !== void 0 ? this.$(t) : t.nodeType !== void 0 ? this.T(t) : St(t) ? this.k(t) : this._(t);
  }
  O(t) {
    return this._$AA.parentNode.insertBefore(t, this._$AB);
  }
  T(t) {
    this._$AH !== t && (this._$AR(), this._$AH = this.O(t));
  }
  _(t) {
    this._$AH !== p && R(this._$AH) ? this._$AA.nextSibling.data = t : this.T(b.createTextNode(t)), this._$AH = t;
  }
  $(t) {
    var o;
    const { values: e, _$litType$: s } = t, i = typeof s == "number" ? this._$AC(t) : (s.el === void 0 && (s.el = M.createElement(ut(s.h, s.h[0]), this.options)), s);
    if (((o = this._$AH) == null ? void 0 : o._$AD) === i) this._$AH.p(e);
    else {
      const n = new Pt(i, this), a = n.u(this.options);
      n.p(e), this.T(a), this._$AH = n;
    }
  }
  _$AC(t) {
    let e = at.get(t.strings);
    return e === void 0 && at.set(t.strings, e = new M(t)), e;
  }
  k(t) {
    G(this._$AH) || (this._$AH = [], this._$AR());
    const e = this._$AH;
    let s, i = 0;
    for (const o of t) i === e.length ? e.push(s = new H(this.O(O()), this.O(O()), this, this.options)) : s = e[i], s._$AI(o), i++;
    i < e.length && (this._$AR(s && s._$AB.nextSibling, i), e.length = i);
  }
  _$AR(t = this._$AA.nextSibling, e) {
    var s;
    for ((s = this._$AP) == null ? void 0 : s.call(this, !1, !0, e); t !== this._$AB; ) {
      const i = et(t).nextSibling;
      et(t).remove(), t = i;
    }
  }
  setConnected(t) {
    var e;
    this._$AM === void 0 && (this._$Cv = t, (e = this._$AP) == null || e.call(this, t));
  }
}
class j {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(t, e, s, i, o) {
    this.type = 1, this._$AH = p, this._$AN = void 0, this.element = t, this.name = e, this._$AM = i, this.options = o, s.length > 2 || s[0] !== "" || s[1] !== "" ? (this._$AH = Array(s.length - 1).fill(new String()), this.strings = s) : this._$AH = p;
  }
  _$AI(t, e = this, s, i) {
    const o = this.strings;
    let n = !1;
    if (o === void 0) t = S(this, t, e, 0), n = !R(t) || t !== this._$AH && t !== w, n && (this._$AH = t);
    else {
      const a = t;
      let h, l;
      for (t = o[0], h = 0; h < o.length - 1; h++) l = S(this, a[s + h], e, h), l === w && (l = this._$AH[h]), n || (n = !R(l) || l !== this._$AH[h]), l === p ? t = p : t !== p && (t += (l ?? "") + o[h + 1]), this._$AH[h] = l;
    }
    n && !i && this.j(t);
  }
  j(t) {
    t === p ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, t ?? "");
  }
}
class Ut extends j {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(t) {
    this.element[this.name] = t === p ? void 0 : t;
  }
}
class Ot extends j {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(t) {
    this.element.toggleAttribute(this.name, !!t && t !== p);
  }
}
class Rt extends j {
  constructor(t, e, s, i, o) {
    super(t, e, s, i, o), this.type = 5;
  }
  _$AI(t, e = this) {
    if ((t = S(this, t, e, 0) ?? p) === w) return;
    const s = this._$AH, i = t === p && s !== p || t.capture !== s.capture || t.once !== s.once || t.passive !== s.passive, o = t !== p && (s === p || i);
    i && this.element.removeEventListener(this.name, this, s), o && this.element.addEventListener(this.name, this, t), this._$AH = t;
  }
  handleEvent(t) {
    var e;
    typeof this._$AH == "function" ? this._$AH.call(((e = this.options) == null ? void 0 : e.host) ?? this.element, t) : this._$AH.handleEvent(t);
  }
}
class Mt {
  constructor(t, e, s) {
    this.element = t, this.type = 6, this._$AN = void 0, this._$AM = e, this.options = s;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(t) {
    S(this, t);
  }
}
const W = P.litHtmlPolyfillSupport;
W == null || W(M, H), (P.litHtmlVersions ?? (P.litHtmlVersions = [])).push("3.3.3");
const Ht = (r, t, e) => {
  const s = (e == null ? void 0 : e.renderBefore) ?? t;
  let i = s._$litPart$;
  if (i === void 0) {
    const o = (e == null ? void 0 : e.renderBefore) ?? null;
    s._$litPart$ = i = new H(t.insertBefore(O(), o), o, void 0, e ?? {});
  }
  return i._$AI(r), i;
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const A = globalThis;
class U extends E {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    var e;
    const t = super.createRenderRoot();
    return (e = this.renderOptions).renderBefore ?? (e.renderBefore = t.firstChild), t;
  }
  update(t) {
    const e = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(t), this._$Do = Ht(e, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    var t;
    super.connectedCallback(), (t = this._$Do) == null || t.setConnected(!0);
  }
  disconnectedCallback() {
    var t;
    super.disconnectedCallback(), (t = this._$Do) == null || t.setConnected(!1);
  }
  render() {
    return w;
  }
}
var ht;
U._$litElement$ = !0, U.finalized = !0, (ht = A.litElementHydrateSupport) == null || ht.call(A, { LitElement: U });
const B = A.litElementPolyfillSupport;
B == null || B({ LitElement: U });
(A.litElementVersions ?? (A.litElementVersions = [])).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Nt = { attribute: !0, type: String, converter: L, reflect: !1, hasChanged: F }, Tt = (r = Nt, t, e) => {
  const { kind: s, metadata: i } = e;
  let o = globalThis.litPropertyMetadata.get(i);
  if (o === void 0 && globalThis.litPropertyMetadata.set(i, o = /* @__PURE__ */ new Map()), s === "setter" && ((r = Object.create(r)).wrapped = !0), o.set(e.name, r), s === "accessor") {
    const { name: n } = e;
    return { set(a) {
      const h = t.get.call(this);
      t.set.call(this, a), this.requestUpdate(n, h, r, !0, a);
    }, init(a) {
      return a !== void 0 && this.C(n, void 0, r, a), a;
    } };
  }
  if (s === "setter") {
    const { name: n } = e;
    return function(a) {
      const h = this[n];
      t.call(this, a), this.requestUpdate(n, h, r, !0, a);
    };
  }
  throw Error("Unsupported decorator location: " + s);
};
function J(r) {
  return (t, e) => typeof e == "object" ? Tt(r, t, e) : ((s, i, o) => {
    const n = i.hasOwnProperty(o);
    return i.constructor.createProperty(o, s), n ? Object.getOwnPropertyDescriptor(i, o) : void 0;
  })(r, t, e);
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function Z(r) {
  return J({ ...r, state: !0, attribute: !1 });
}
var kt = Object.defineProperty, N = (r, t, e, s) => {
  for (var i = void 0, o = r.length - 1, n; o >= 0; o--)
    (n = r[o]) && (i = n(t, e, i) || i);
  return i && kt(t, e, i), i;
};
const K = class K extends U {
  constructor() {
    super(...arguments), this._floors = [], this._areas = [], this._dataLoaded = !1;
  }
  setConfig(t) {
    this.config = t;
  }
  async updated(t) {
    if (super.updated(t), t.has("hass") && this.hass && !this._dataLoaded) {
      this._dataLoaded = !0;
      try {
        this._floors = await this.hass.callWS({ type: "config/floor_registry/list" }), this._areas = await this.hass.callWS({ type: "config/area_registry/list" });
      } catch (e) {
        console.error("Neuro Rooms: Failed to fetch floors/areas", e);
      }
    }
  }
  getStubLayout() {
    const t = Object.values(this.hass.states).filter(
      (a) => a.entity_id.startsWith("sensor.") && a.attributes.room_config !== void 0
    ), e = /* @__PURE__ */ new Map(), s = [];
    t.forEach((a) => {
      const l = (a.attributes.room_config || {}).area_id;
      l ? (e.has(l) || e.set(l, []), e.get(l).push(a)) : s.push(a);
    });
    const i = /* @__PURE__ */ new Map(), o = [];
    return e.forEach((a, h) => {
      const l = this._areas.find((c) => c.area_id === h);
      l && l.floor_id ? (i.has(l.floor_id) || i.set(l.floor_id, []), i.get(l.floor_id).push({ area: l, rooms: a })) : o.push({ area: l || { name: "Unknown Area" }, rooms: a });
    }), { sortedFloors: [...this._floors].filter((a) => i.has(a.floor_id)).sort((a, h) => (a.level || 0) - (h.level || 0)), floorsWithAreas: i, unassignedAreas: o, unassignedRooms: s };
  }
  render() {
    if (!this.hass || !this._dataLoaded) return v`<ha-card><div style="padding:16px;">Loading...</div></ha-card>`;
    const { sortedFloors: t, floorsWithAreas: e, unassignedAreas: s, unassignedRooms: i } = this.getStubLayout();
    return v`
      <ha-card>
        <div class="header">Neuro Rooms</div>
        
        ${t.map((o) => v`
          <div class="floor">
            <div class="floor-name">${o.name}</div>
            <div class="areas">
              ${e.get(o.floor_id).map((n) => this.renderAreaGroup(n))}
            </div>
          </div>
        `)}

        ${s.length > 0 ? v`
          <div class="floor">
            <div class="floor-name">Unassigned Areas</div>
            <div class="areas">
              ${s.map((o) => this.renderAreaGroup(o))}
            </div>
          </div>
        ` : ""}

        ${i.length > 0 ? v`
          <div class="floor">
            <div class="floor-name">Unassigned Rooms</div>
            <div class="areas">
              ${i.map((o) => this.renderRoom(o))}
            </div>
          </div>
        ` : ""}
      </ha-card>
    `;
  }
  renderAreaGroup(t) {
    return v`
      ${t.rooms.map((e) => this.renderRoom(e, t.area.name))}
    `;
  }
  renderRoom(t, e) {
    const i = (t.attributes.room_config || {}).name || e || t.attributes.room_id || "Unknown Room", o = t.state, n = { ...t.attributes };
    return delete n.friendly_name, delete n.icon, v`
      <div class="room-card">
        <div class="room-header">
          <div class="room-name">${i}</div>
          <div class="room-state ${o}">${o}</div>
        </div>
        <div class="room-details">
          <details>
            <summary>Parameters / State</summary>
            <pre>${JSON.stringify(n, null, 2)}</pre>
          </details>
        </div>
      </div>
    `;
  }
};
K.styles = $t`
    ha-card {
      padding: 16px;
    }
    .header {
      font-size: 1.2rem;
      font-weight: bold;
      margin-bottom: 16px;
    }
    .floor {
      margin-bottom: 24px;
    }
    .floor-name {
      font-size: 1.1rem;
      font-weight: 500;
      border-bottom: 1px solid var(--divider-color, #ccc);
      padding-bottom: 4px;
      margin-bottom: 12px;
      color: var(--primary-color);
    }
    .areas {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }
    .room-card {
      border: 1px solid var(--divider-color, #ccc);
      border-radius: 8px;
      padding: 12px;
      background: var(--card-background-color, #fff);
    }
    .room-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .room-name {
      font-weight: 600;
    }
    .room-state {
      background: var(--primary-color);
      color: var(--text-primary-color, white);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.8rem;
      text-transform: uppercase;
    }
    .room-state.idle { background: var(--label-badge-grey, #9e9e9e); }
    .room-state.occupied { background: var(--label-badge-red, #f44336); }
    .room-state.night { background: var(--label-badge-blue, #03a9f4); }
    .room-state.away { background: var(--label-badge-yellow, #ffeb3b); color: black; }
    
    .room-details {
      font-size: 0.85rem;
      color: var(--secondary-text-color);
    }
    .room-details pre {
      background: var(--secondary-background-color);
      padding: 8px;
      border-radius: 4px;
      overflow-x: auto;
      margin-top: 8px;
      font-size: 0.75rem;
    }
  `;
let m = K;
N([
  J({ attribute: !1 })
], m.prototype, "hass");
N([
  J({ attribute: !1 })
], m.prototype, "config");
N([
  Z()
], m.prototype, "_floors");
N([
  Z()
], m.prototype, "_areas");
N([
  Z()
], m.prototype, "_dataLoaded");
customElements.define("neuro-rooms-card", m);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "neuro-rooms-card",
  name: "Neuro Rooms Card",
  description: "Displays hierarchy of floors and neuro rooms"
});
export {
  m as NeuroRoomsCard
};
