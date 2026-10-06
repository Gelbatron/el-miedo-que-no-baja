"use client";
import { useEffect, useRef } from "react";

// Un solo tooltip para todo el visor: cualquier elemento con data-tip lo activa (mouse, toque y teclado).
export function Tooltip() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const tip = ref.current!;
    const mostrar = (el: Element, x: number, y: number) => {
      tip.innerHTML = el.getAttribute("data-tip") ?? "";
      tip.hidden = false;
      const w = tip.offsetWidth, h = tip.offsetHeight;
      let left = x + 14, top = y + 14;
      if (left + w > window.innerWidth - 8) left = x - w - 14;
      if (top + h > window.innerHeight - 8) top = y - h - 14;
      tip.style.left = `${Math.max(8, left)}px`;
      tip.style.top = `${Math.max(8, top)}px`;
    };
    const mover = (e: PointerEvent) => {
      const el = (e.target as Element)?.closest?.("[data-tip]");
      if (!el) { tip.hidden = true; return; }
      mostrar(el, e.clientX, e.clientY);
    };
    const foco = (e: FocusEvent) => {
      const el = (e.target as Element)?.closest?.("[data-tip]");
      if (!el) return;
      const r = el.getBoundingClientRect();
      mostrar(el, r.right, r.top);
    };
    const ocultar = () => { tip.hidden = true; };
    window.addEventListener("pointermove", mover);
    window.addEventListener("focusin", foco);
    window.addEventListener("focusout", ocultar);
    window.addEventListener("scroll", ocultar, { passive: true });
    return () => {
      window.removeEventListener("pointermove", mover);
      window.removeEventListener("focusin", foco);
      window.removeEventListener("focusout", ocultar);
      window.removeEventListener("scroll", ocultar);
    };
  }, []);
  return <div id="tip" ref={ref} hidden role="tooltip" />;
}
