/*
 * Xoxoday PPTX theme — reusable pptxgenjs palette + slide helpers.
 *
 * Setup:  npm install pptxgenjs
 * Usage:
 *   const pptxgen = require("pptxgenjs");
 *   const X = require("./pptx_theme.js");
 *   const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
 *   const t = X.bind(pres);                       // bind helpers to this presentation
 *   let s = t.titleSlide("AI won't solve your problem. You will.", "Subtitle here", "Abhimanyu Singh");
 *   s = pres.addSlide(); s.background = { color: X.LIGHT };
 *   t.kicker(s, "Part 1 · Where AI works"); t.title(s, "Use AI where you know the answer");
 *   t.card(s, { x:0.9, y:2.6, w:3.85, h:3.0, title:"The product marketer", body:"…" });
 *   t.brandTag(s, false);
 *   pres.writeFile({ fileName: "deck.pptx" });
 *
 * To rebrand: edit the hex values below (they are also documented in SKILL.md).
 */
const INK = "1B1530", PANEL = "2A1E47", CORAL = "F4593F", CORALL = "FB7A63",
      PLUM = "7A3D9C", GOLD = "FFBC2E", CLOUD = "F6F4FA", WHITE = "FFFFFF",
      SLATE = "6B6480", ICE = "D9D2EA", MUTE = "9B92B5";
const WIN = "27B98A", CAUTION = "FFBC2E", RISK = "F4593F";
const HEAD = "Trebuchet MS", BODY = "Calibri";
const shadow = () => ({ type: "outer", color: "1B1530", blur: 9, offset: 3, angle: 135, opacity: 0.18 });

function bind(pres) {
  const S = pres.shapes;
  const rings = (s) => {
    s.addShape(S.OVAL, { x: 10.2, y: -2.3, w: 6, h: 6, fill: { type: "none" }, line: { color: PLUM, width: 1.25, transparency: 45 } });
    s.addShape(S.OVAL, { x: 11.0, y: -1.5, w: 4, h: 4, fill: { type: "none" }, line: { color: CORAL, width: 1.25, transparency: 30 } });
    s.addShape(S.OVAL, { x: -1.4, y: 5.2, w: 4.5, h: 4.5, fill: { type: "none" }, line: { color: GOLD, width: 1.25, transparency: 55 } });
  };
  const kicker = (s, t, x = 0.9, y = 0.6, c = CORAL) =>
    s.addText(String(t).toUpperCase(), { x, y, w: 10, h: 0.32, margin: 0, fontFace: HEAD, fontSize: 12.5, bold: true, color: c, charSpacing: 3 });
  const title = (s, t, c = INK, y = 0.95, size = 33) =>
    s.addText(t, { x: 0.85, y, w: 11.9, h: 0.85, fontFace: HEAD, fontSize: size, bold: true, color: c });
  const brandTag = (s, dark, label = "How I AI") =>
    s.addText([{ text: "XOXODAY", options: { bold: true, color: dark ? MUTE : SLATE, charSpacing: 2 } }, { text: "  ·  " + label, options: { color: dark ? MUTE : SLATE } }],
      { x: 10.4, y: 7.0, w: 2.7, h: 0.32, align: "right", margin: 0, fontFace: BODY, fontSize: 9 });
  const card = (s, o) => { // {x,y,w,h,title,body,accent,dark,kicker}
    const dark = !!o.dark, acc = o.accent || CORAL;
    s.addShape(S.RECTANGLE, { x: o.x, y: o.y, w: o.w, h: o.h, fill: { color: dark ? PANEL : WHITE }, line: { type: "none" }, shadow: shadow() });
    s.addShape(S.RECTANGLE, { x: o.x, y: o.y, w: 0.1, h: o.h, fill: { color: acc } });
    let ty = o.y + 0.28;
    if (o.kicker) { s.addText(String(o.kicker).toUpperCase(), { x: o.x + 0.35, y: ty, w: o.w - 0.6, h: 0.3, margin: 0, fontFace: HEAD, fontSize: 11, bold: true, color: acc, charSpacing: 2 }); ty += 0.34; }
    if (o.title) { s.addText(o.title, { x: o.x + 0.35, y: ty, w: o.w - 0.6, h: 0.55, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: dark ? WHITE : INK }); ty += 0.6; }
    if (o.body) s.addText(o.body, { x: o.x + 0.35, y: ty + 0.05, w: o.w - 0.6, h: o.y + o.h - ty - 0.3, margin: 0, fontFace: BODY, fontSize: 14, color: dark ? ICE : SLATE });
  };
  const statCard = (s, o) => { // {x,y,w,h,stat,label,note,accent,dark}
    const dark = o.dark !== false, acc = o.accent || GOLD;
    s.addShape(S.RECTANGLE, { x: o.x, y: o.y, w: o.w, h: o.h, fill: { color: dark ? PANEL : WHITE }, line: { type: "none" }, shadow: shadow() });
    s.addShape(S.RECTANGLE, { x: o.x, y: o.y, w: o.w, h: 0.12, fill: { color: acc } });
    s.addText(o.stat, { x: o.x + 0.3, y: o.y + 0.4, w: o.w - 0.6, h: 0.9, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: acc });
    if (o.label) s.addText(String(o.label).toUpperCase(), { x: o.x + 0.3, y: o.y + 1.35, w: o.w - 0.6, h: 0.4, margin: 0, fontFace: BODY, fontSize: 12, bold: true, color: dark ? WHITE : INK, charSpacing: 1 });
    if (o.note) s.addText(o.note, { x: o.x + 0.3, y: o.y + 1.8, w: o.w - 0.6, h: o.h - 1.95, margin: 0, fontFace: BODY, fontSize: 13.5, color: dark ? ICE : SLATE });
  };
  const askRoom = (s, q, x = 0.9, y = 6.2, w = 11.5) => {
    s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h: 0.85, rectRadius: 0.1, fill: { color: PLUM }, line: { type: "none" }, shadow: shadow() });
    s.addShape(S.OVAL, { x: x + 0.22, y: y + 0.22, w: 0.42, h: 0.42, fill: { color: CORAL } });
    s.addText("?", { x: x + 0.22, y: y + 0.2, w: 0.42, h: 0.42, align: "center", valign: "middle", margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: WHITE });
    s.addText([{ text: "ASK THE ROOM   ", options: { bold: true, color: GOLD, fontSize: 11, charSpacing: 2 } }, { text: q, options: { color: WHITE, fontSize: 14.5 } }],
      { x: x + 0.85, y, w: w - 1.1, h: 0.85, valign: "middle", margin: 0, fontFace: BODY });
  };
  const titleSlide = (headline, sub, name, role) => {
    const s = pres.addSlide(); s.background = { color: INK }; rings(s);
    kicker(s, "How I AI at Xoxoday", 0.9, 1.3, CORAL);
    s.addText(headline, { x: 0.85, y: 1.75, w: 11.4, h: 2.0, fontFace: HEAD, fontSize: 46, bold: true, color: WHITE, lineSpacing: 50 });
    if (sub) s.addText(sub, { x: 0.9, y: 3.95, w: 10.4, h: 0.9, fontFace: BODY, fontSize: 17, color: ICE });
    s.addShape(S.RECTANGLE, { x: 0.9, y: 5.6, w: 0.07, h: 1.0, fill: { color: CORAL } });
    if (name) s.addText([{ text: name, options: { bold: true, color: WHITE, fontSize: 16, breakLine: true } }, { text: role || "", options: { color: ICE, fontSize: 13 } }],
      { x: 1.18, y: 5.6, w: 7, h: 1.0, valign: "middle", margin: 0, fontFace: BODY });
    return s;
  };
  return { rings, kicker, title, brandTag, card, statCard, askRoom, titleSlide };
}

module.exports = { bind, INK, PANEL, CORAL, CORALL, PLUM, GOLD, CLOUD, WHITE, SLATE, ICE, MUTE, WIN, CAUTION, RISK, HEAD, BODY, shadow };
