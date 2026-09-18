import base64
from io import BytesIO
from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component("camera_live", path=str(frontend_dir))


def camera_live(
    facing: str = "user",
    debounce_ms: int = 300,
    height: int = 480,
    width: int = 640,
    show_controls: bool = True,
    start_label: str = "Start capturing",
    stop_label: str = "Pause capturing",
    key: Optional[str] = None,
) -> Optional[BytesIO]:
    b64_data: Optional[str] = _component_func(
        facing=facing,
        debounceMs=debounce_ms,
        height=height,
        width=width,
        showControls=show_controls,
        startLabel=start_label,
        stopLabel=stop_label,
        key=key,
    )
    if b64_data is None:
        return None
    raw_data = b64_data.split(",", 1)[1]
    return BytesIO(base64.b64decode(raw_data))


if __name__ == "__main__":
    st.write("## Example")
    image = camera_live()
    if image is not None:
        st.image(image)