from pathlib import Path
import base64
import io
import json

import av
import numpy as np
import streamlit as st
from PIL import Image, ImageOps
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer
from tensorflow import keras

from vision import PROJECT_DIR, CatDetector, IMAGE_SIZE, annotate

CLASS_NAMES_PATH = PROJECT_DIR / "models" / "class_names.json"
MODEL_PATH = PROJECT_DIR / "models" / "meko_lily.keras"

UPGRADED = {"meko": "Meko", "lily": "Lily", "other": "A visitor"}
FIRM_BOX = 0.75
FIRM_PHOTO = 0.70

st.set_page_config(page_title="Meko or Lily?", page_icon="🐱", layout="centered")

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#f3ead9; --paper-2:#eadcc2; --paper-ink:#1e2a24;
  --ink-soft:rgba(30,42,36,.80); --ink-faint:rgba(30,42,36,.68);
  --green:#2e6b4f; --green-deep:#1f4f3a; --gold:#5f5230; --gold-soft:#8a7a5c;
  --red-ink:#b04a2f;
  --display:'Archivo','Segoe UI',Arial,sans-serif;
  --book:'Source Serif 4',Georgia,'Times New Roman',serif;
}
.stApp{background:var(--paper);color:var(--paper-ink);font-family:var(--book);}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.6rem;padding-bottom:2rem;}
p,li,span,div{color:inherit;}
.masthead{margin-bottom:.4rem;}
.book-title{font-family:var(--display);font-weight:700;font-size:2.35rem;letter-spacing:.02em;margin:0;color:var(--paper-ink);}
.book-sub{margin:.15rem 0 .9rem;font-size:1.02rem;color:var(--ink-soft);}
.binding{border-top:2px solid var(--ink);border-bottom:1px solid var(--ink);height:4px;margin-bottom:1.1rem;position:relative;}
.binding::after{content:"";position:absolute;left:50%;top:-3px;transform:translateX(-50%);width:9px;height:9px;background:var(--paper);border:1px solid var(--ink);transform-origin:50% 40%;rotate:45deg;}
[data-testid="column"]{background:var(--paper-2);border:1px solid rgba(30,42,36,.12);padding:1.05rem 1.2rem 1.2rem;border-radius:2px;}
[data-testid="stHorizontalBlock"]{position:relative;gap:1.1rem;}
[data-testid="stHorizontalBlock"]::after{content:"";position:absolute;left:50%;top:1rem;bottom:1rem;width:2px;background:repeating-linear-gradient(var(--gold-soft) 0 4px,transparent 4px 9px);opacity:.35;}
@media (max-width:720px){[data-testid="stHorizontalBlock"]{flex-direction:column;}[data-testid="stHorizontalBlock"]::after{display:none;}}
.mount{position:relative;background:var(--paper);padding:14px;border:1px solid rgba(30,42,36,.18);min-height:230px;display:flex;align-items:center;justify-content:center;}
.mount img{max-width:100%;height:auto;display:block;border:1px solid rgba(30,42,36,.15);}
.mount-empty{font-family:var(--display);font-weight:500;text-align:center;color:var(--ink-faint);letter-spacing:.06em;font-size:.92rem;line-height:1.7;}
.corner{position:absolute;width:18px;height:18px;border:2px solid var(--gold-soft);opacity:.85;}
.corner.tl{top:5px;left:5px;border-right:none;border-bottom:none;}
.corner.tr{top:5px;right:5px;border-left:none;border-bottom:none;}
.corner.bl{bottom:5px;left:5px;border-right:none;border-top:none;}
.corner.br{bottom:5px;right:5px;border-left:none;border-top:none;}
.nameplate{margin-top:.7rem;display:flex;flex-direction:column;align-items:center;gap:.15rem;text-align:center;}
.nameplate span{font-family:var(--display);font-weight:700;letter-spacing:.28em;font-size:1.05rem;color:var(--paper-ink);}
.nameplate small{font-family:var(--book);font-style:italic;color:var(--ink-soft);font-size:.86rem;}
.legend{margin-top:.8rem;display:flex;gap:.9rem;justify-content:center;flex-wrap:wrap;}
.legend span{font-family:var(--display);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);display:flex;align-items:center;gap:.35rem;}
.legend i{width:11px;height:11px;border:1px solid rgba(30,42,36,.35);display:inline-block;}
.legend i.meko{background:#38b04a;}
.legend i.lily{background:#ff9d2e;}
.legend i.other{background:#a9a89f;}
.plate{padding-top:.15rem;}
.plate-label{font-family:var(--display);font-weight:600;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);}
.stamp{margin:1rem 0 .4rem;display:inline-block;padding:.55rem 1.05rem;border:3px double var(--green-deep);color:var(--green-deep);font-family:var(--display);font-weight:700;text-transform:uppercase;letter-spacing:.18em;font-size:2.05rem;line-height:1.15;position:relative;box-shadow:inset 0 0 0 2px rgba(47,107,79,.18);}
@keyframes stamp-clack{0%{transform:scale(2.2) rotate(-9deg);opacity:0;}60%{transform:scale(1.04) rotate(.4deg);opacity:1;}82%{transform:scale(.98) rotate(-.2deg);}100%{transform:scale(1) rotate(0);}}
.stamp .ink{display:inline-block;animation:stamp-clack .32s cubic-bezier(.22,1,.36,1) both;}
.stamp-denied{color:var(--red-ink);border-color:var(--red-ink);transform:rotate(-3.5deg);box-shadow:inset 0 0 0 2px rgba(179,74,46,.15);}
.stamp-denied .ink{text-transform:uppercase;}
.stamp-doubt .ink{animation-name:stamp-tilt;}
@keyframes stamp-tilt{0%{transform:scale(1.25) rotate(6deg);opacity:0;}100%{transform:scale(1) rotate(0);opacity:.92;}}
.stamp-doubt{box-shadow:inset 0 0 0 2px rgba(30,42,36,.12);color:var(--paper-ink);border-color:var(--ink-soft);}
.stamp-seam{display:inline-flex;align-items:stretch;gap:0;padding:0;border:3px double var(--green-deep);color:var(--green-deep);overflow:hidden;animation:stamp-clack .32s cubic-bezier(.22,1,.36,1) both;}
.stamp-seam .half{padding:.55rem .5rem;}
.stamp-seam .half.right{color:var(--green-deep);}
.stamp-seam .seam{width:3px;background:repeating-linear-gradient(var(--gold-soft) 0 3px,transparent 3px 7px);}
.ink-note{font-family:var(--book);color:var(--ink-soft);font-size:1rem;line-height:1.55;margin:.35rem 0 0;max-width:34ch;}
.ink-note .conf{font-family:var(--display);font-weight:600;font-size:.8rem;letter-spacing:.06em;color:var(--green-deep);white-space:nowrap;}
.plate-empty p{margin-top:1.6rem;}
details.flap{margin-top:1.25rem;border-top:1px dashed rgba(30,42,36,.3);padding-top:.7rem;}
details.flap summary{cursor:pointer;font-family:var(--display);font-weight:600;font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ink-soft);list-style:none;}
details.flap summary::-webkit-details-marker{display:none;}
details.flap summary::after{content:"+";float:right;color:var(--gold-soft);font-weight:700;}
details.flap[open] summary::after{content:"–";}
details.flap .row{display:flex;align-items:center;gap:.6rem;margin-top:.6rem;font-family:var(--display);font-size:.8rem;letter-spacing:.04em;color:var(--paper-ink);}
details.flap .row .pct{margin-left:auto;color:var(--ink-soft);font-variant-numeric:tabular-nums;}
details.flap .row .bar{height:6px;flex:1 1 auto;max-width:220px;background:rgba(30,42,36,.1);border:1px solid rgba(30,42,36,.25);}
details.flap[open] .row .bar{background:linear-gradient(90deg,var(--green) var(--filled,0%),rgba(30,42,36,.1) var(--filled,0%));}
.stRadio{display:flex;justify-content:stretch;margin:0 -.1rem .6rem;overflow-x:auto;}
div[role="radiogroup"]{flex-wrap:wrap-reverse;}
.stRadio label{flex:1 1 auto;min-width:120px;margin:0;padding:.55rem .5rem;text-align:center;font-family:var(--display);font-weight:600;font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);border-bottom:2px solid rgba(30,42,36,.18);cursor:pointer;transition:color .12s ease,background-color .12s ease,border-color .12s ease;}
.stRadio label:has(input:checked){color:var(--paper);background:var(--green);border-bottom-color:var(--green-deep);}
.stRadio label:hover{color:var(--green-deep);}
.stRadio input{position:absolute;opacity:0;pointer-events:none;}
.stRadio label p{margin:0;font-family:inherit;font-weight:inherit;letter-spacing:inherit;color:inherit;}
.stFileUploader section, [data-testid="stCameraInput"]{background:var(--paper);border:1px solid rgba(30,42,36,.22);border-radius:2px;}
.stFileUploader button{font-family:var(--display);letter-spacing:.06em;}
label[for] input, textarea{caret-color:var(--green-deep);}
.widget-hint{font-family:var(--book);font-style:italic;color:var(--ink-soft);font-size:.92rem;margin:.1rem 0 1rem;}
*:focus-visible{outline:2px solid var(--green-deep);outline-offset:2px;}
::selection{background:var(--green-deep);color:var(--paper);}
::-webkit-scrollbar{width:10px;height:10px;}
::-webkit-scrollbar-thumb{background:rgba(47,107,79,.35);border-radius:6px;}
::-webkit-scrollbar-track{background:var(--paper);}
.live-note{margin-top:.8rem;font-family:var(--book);line-height:1.6;color:var(--ink-soft);}
.live-trace{display:flex;align-items:center;gap:.6rem;margin-top:.85rem;font-family:var(--display);font-weight:600;font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--green-deep);}
.live-trace .tr{width:2px;height:44px;background:linear-gradient(var(--red-ink) 0%,var(--gold-soft) 55%,var(--green-deep) 100%);border-radius:2px;}
.live-on{display:flex;align-items:center;gap:.5rem;font-family:var(--display);font-weight:600;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--green-deep);margin-left:auto;}
.live-dot{width:9px;height:9px;border-radius:50%;background:var(--red-ink);animation:live .9s ease-in-out infinite alternate;}
@keyframes live{from{opacity:1;}to{opacity:.25;}}
.footer{margin-top:1.7rem;border-top:1px solid rgba(30,42,36,.15);padding-top:.8rem;font-family:var(--book);font-size:.85rem;color:var(--ink-faint);text-align:center;}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important;}
  .stamp .ink{animation:none;opacity:1;}
}
</style>
"""


def data_uri(image: Image.Image, max_side=1100) -> str:
    thumb = image.copy()
    thumb.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=86)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def photo_mount(data_uri: str | None) -> str:
    if data_uri:
        inner = f'<img src="{data_uri}" alt="The cat on this page" />'
    else:
        inner = '<p class="mount-empty">The page is blank.<br />Add a photo or open the camera.</p>'
    return (
        '<div class="mount">'
        '<i class="corner tl"></i><i class="corner tr"></i>'
        '<i class="corner bl"></i><i class="corner br"></i>'
        + inner
        + "</div>"
    )


def nameplate() -> str:
    return (
        '<div class="nameplate">'
        "<span>MEKO &middot; LILY</span>"
        "<small>the registered pair</small>"
        "</div>"
    )


def legend() -> str:
    return (
        '<div class="legend">'
        '<span><i class="meko"></i>Meko</span>'
        '<span><i class="lily"></i>Lily</span>'
        '<span><i class="other"></i>A visitor</span>'
        "</div>"
    )


def stamp_block(kind: str, main: str, alt: str | None = None) -> str:
    if kind == "seam":
        ink = (
            f'<span class="half left">{main}</span>'
            '<span class="seam"></span>'
            f'<span class="half right">{alt}</span>'
        )
    else:
        ink = f'<span class="ink">{main}</span>'
    return f'<div class="stamp stamp-{kind}">{ink}</div>'


def plate(kind: str, main: str, conf: float | None = None, note: str = "", rows=None, alt: str | None = None) -> str:
    stamp = stamp_block(kind, main, alt)
    conf_html = f' <span class="conf">&middot; {conf:.0%} sure</span>' if conf is not None else ""
    rows_html = ""
    if rows:
        pieces = []
        for name, prob in rows:
            pieces.append(
                f'<div class="row"><span>{name}</span>'
                f'<span class="bar" style="--filled:{prob:.0%}"></span>'
                f'<span class="pct">{prob:.1%}</span></div>'
            )
        rows_html = (
            '<details class="flap"><summary>The ledger&rsquo;s numbers</summary>'
            + "".join(pieces)
            + "</details>"
        )
    return (
        '<div class="plate">'
        '<span class="plate-label">THE VERDICT</span>'
        + stamp
        + f'<p class="ink-note">{note}{conf_html}</p>'
        + rows_html
        + "</div>"
    )


def probs_of(model, bgr) -> np.ndarray:
    rgb = np.ascontiguousarray(bgr[:, :, ::-1])
    image = Image.fromarray(rgb).resize(IMAGE_SIZE)
    pixels = np.asarray(image, dtype=np.uint8)[None, ...]
    return 0.5 * (
        model.predict(pixels, verbose=0)[0] + model.predict(np.flip(pixels, axis=2), verbose=0)[0]
    )


def resolve_verdict(model, class_names, frame_bgr, results):
    names = [UPGRADED.get(name, name.title()) for name in class_names]
    if results:
        known = [r for r in results if r["label"] != "other cat"]
        if known:
            chosen = max(known, key=lambda r: r["confidence"])
            x1, y1, x2, y2 = chosen["box"]
            crop = frame_bgr[y1:y2, x1:x2]
            probs = probs_of(model, crop) if crop.size else None
            rows = [(names[i], float(probs[i])) for i in range(len(class_names))] if probs is not None else None
            if len(results) > 1:
                others = ", ".join(f"{r['label']} {r['confidence']:.0%}" for r in results if r != chosen)
                note = f"Two cats on the page ({others}) &mdash; this stamp picks the closest match."
            else:
                note = "Read from a box drawn around the cat."
            kind = "name" if chosen["confidence"] >= FIRM_BOX else "doubt"
            return {"kind": kind, "main": chosen["label"], "alt": None,
                    "conf": chosen["confidence"], "note": note, "rows": rows}
        strangers = ", ".join(f"{r['label']} {r['confidence']:.0%}" for r in results)
        note = f"The boxed cat{'' if len(results) == 1 else 's'} ({strangers}) "
        note += "has no page in the book &mdash; looks like a visitor."
        return {"kind": "denied", "main": "Not registered", "alt": None, "conf": None,
                "note": note, "rows": None}
    probs = probs_of(model, frame_bgr)
    order = sorted(range(len(class_names)), key=lambda i: probs[i], reverse=True)
    best = order[0]
    name = UPGRADED.get(class_names[best], class_names[best].title())
    conf = float(probs[best])
    rows = [(names[i], float(probs[i])) for i in range(len(class_names))]
    if class_names[best] == "other":
        return {"kind": "denied", "main": "Not registered", "alt": None, "conf": None,
                "note": "The cat stayed out of focus &mdash; the book still refuses to name it.", "rows": rows}
    if conf >= FIRM_PHOTO:
        return {"kind": "name", "main": name, "alt": None, "conf": conf,
                "note": "Read from the whole photo; no cat filled a box, so take it as a light note.", "rows": rows}
    if probs[order[0]] - probs[order[1]] >= 0.08:
        return {"kind": "doubt", "main": name, "alt": None, "conf": conf,
                "note": "Seen from across the room &mdash; the stamp won&rsquo;t seat. Try a closer, brighter photo.", "rows": rows}
    second = UPGRADED.get(class_names[order[1]], class_names[order[1]].title())
    return {"kind": "seam", "main": name, "alt": second, "conf": None,
            "note": "The page split between two cats &mdash; it&rsquo;s one or the other.", "rows": rows}


@st.cache_resource
def load_assets():
    model = keras.models.load_model(MODEL_PATH)
    class_names = json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))
    detector = CatDetector()
    return model, class_names, detector


class CatVideoProcessor(VideoProcessorBase):
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image_bgr = frame.to_ndarray(format="bgr24")
        annotated, _ = annotate(image_bgr, model, class_names, detector)
        return av.VideoFrame.from_ndarray(annotated, format="bgr24")


st.markdown(CSS, unsafe_allow_html=True)

if not MODEL_PATH.exists() or not CLASS_NAMES_PATH.exists():
    st.markdown(
        '<div class="plate">'
        '<span class="plate-label">A NOTE FROM THE BOOK</span>'
        '<p class="mount-empty">The book is empty &mdash; it has not met the cats yet.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

model, class_names, detector = load_assets()

st.markdown(
    '<div class="masthead">'
    '<h1 class="book-title">Meko&nbsp;or&nbsp;Lily?</h1>'
    '<p class="book-sub">The cats&rsquo; record book &mdash; show it a cat and it stamps who it is.</p>'
    '<div class="binding"></div>'
    "</div>",
    unsafe_allow_html=True,
)

UPLOAD_TAB = "Upload a photo"
SNAPSHOT_TAB = "Take a snapshot"
LIVE_TAB = "Live camera"

source = st.radio("", (UPLOAD_TAB, SNAPSHOT_TAB, LIVE_TAB), horizontal=True)

if source == LIVE_TAB:
    ctx = webrtc_streamer(
        key="meko-lily-live",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=CatVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )
    watching = bool(ctx and ctx.state.playing)
    if watching:
        st.markdown(
            '<div class="live-trace"><span class="tr"></span>The stamp is live</div>'
            '<div class="live-note"><span class="live-on"><span class="live-dot"></span>Live &mdash; stamping now</span>'
            "&nbsp;every cat in frame is boxed and named as it moves. Watch the colours: green is Meko, orange is Lily, grey is a visitor.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="live-note">Press <b>Start</b> and let the camera in. If the feed stays dark or the camera never '
            "opens, the browser may be refusing it &mdash; <b>Upload a photo</b> or <b>Take a snapshot</b> work on every device.</div>",
            unsafe_allow_html=True,
        )
    st.markdown(legend(), unsafe_allow_html=True)
    st.markdown(
        '<div class="footer">Photos are read once, in the moment &mdash; never saved, never used to retrain.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

photo = None
if source == UPLOAD_TAB:
    photo = st.file_uploader("", type=["jpg", "jpeg", "png"], key="petbook-upload")
    st.markdown(
        '<div class="widget-hint">A photo of one cat, or a whole house of them &mdash; every cat gets boxed and stamped.</div>',
        unsafe_allow_html=True,
    )
elif source == SNAPSHOT_TAB:
    photo = st.camera_input("", key="petbook-snapshot")
    st.markdown(
        '<div class="widget-hint">Hold steady in good light &mdash; the book reads the cat best that way.</div>',
        unsafe_allow_html=True,
    )

verdict = None
annotated_uri = None

if photo is not None:
    image = Image.open(photo).convert("RGB")
    image = ImageOps.exif_transpose(image)
    frame_bgr = np.asarray(image)[:, :, ::-1].copy()
    annotated, results = annotate(frame_bgr, model, class_names, detector)
    verdict = resolve_verdict(model, class_names, frame_bgr, results)
    annotated_uri = data_uri(Image.fromarray(annotated[:, :, ::-1].copy()))

left, right = st.columns([5, 6])

with left:
    st.markdown(photo_mount(annotated_uri), unsafe_allow_html=True)
    st.markdown(nameplate(), unsafe_allow_html=True)
    st.markdown(legend(), unsafe_allow_html=True)

with right:
    if verdict is None:
        st.markdown(
            '<div class="plate plate-empty">'
            '<span class="plate-label">THE VERDICT</span>'
            '<p class="mount-empty">Waiting for a cat&hellip;</p>'
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            plate(verdict["kind"], verdict["main"], conf=verdict["conf"],
                  note=verdict["note"], rows=verdict["rows"], alt=verdict["alt"]),
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="footer">Photos are read once, in the moment &mdash; never saved, never used to retrain.</div>',
    unsafe_allow_html=True,
)