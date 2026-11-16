"""
Biblioteca de Ícones Lucide (SVG Vector) para o StudyFlow.
Garante visual 100% profissional e consistente sem emojis em botões e componentes.
"""

def icon(name: str, size: int = 18, color: str = "currentColor", stroke_width: float = 2.0, extra_class: str = "") -> str:
    """Retorna o SVG inline do ícone Lucide com atributos consistentes."""
    svgs = {
        "logo_cap": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/>'
            '<path d="M6 12v5c3 3 9 3 12 0v-5"/>'
            '</svg>'
        ),
        "layout_dashboard": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<rect width="7" height="9" x="3" y="3" rx="1"/>'
            '<rect width="7" height="5" x="14" y="3" rx="1"/>'
            '<rect width="7" height="9" x="14" y="12" rx="1"/>'
            '<rect width="7" height="5" x="3" y="16" rx="1"/>'
            '</svg>'
        ),
        "book_open": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>'
            '<path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'
            '</svg>'
        ),
        "check_circle": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
            '<polyline points="22 4 12 14.01 9 11.01"/>'
            '</svg>'
        ),
        "clock": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<circle cx="12" cy="12" r="10"/>'
            '<polyline points="12 6 12 12 16 14"/>'
            '</svg>'
        ),
        "calendar": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
            '</svg>'
        ),
        "trending_up": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>'
            '<polyline points="17 6 23 6 23 12"/>'
            '</svg>'
        ),
        "zap": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
            '</svg>'
        ),
        "timer": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<line x1="10" y1="2" x2="14" y2="2"/>'
            '<line x1="12" y1="14" x2="15" y2="11"/>'
            '<circle cx="12" cy="14" r="8"/>'
            '</svg>'
        ),
        "play": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="currentColor" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polygon points="5 3 19 12 5 21 5 3"/>'
            '</svg>'
        ),
        "pause": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<rect x="6" y="4" width="4" height="16"/>'
            '<rect x="14" y="4" width="4" height="16"/>'
            '</svg>'
        ),
        "coffee": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M18 8h1a4 4 0 0 1 0 8h-1"/>'
            '<path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>'
            '<line x1="6" y1="1" x2="6" y2="4"/>'
            '<line x1="10" y1="1" x2="10" y2="4"/>'
            '<line x1="14" y1="1" x2="14" y2="4"/>'
            '</svg>'
        ),
        "rotate_ccw": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>'
            '<path d="M3 3v5h5"/>'
            '</svg>'
        ),
        "arrow_right": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<line x1="5" y1="12" x2="19" y2="12"/>'
            '<polyline points="12 5 19 12 12 19"/>'
            '</svg>'
        ),
        "chevron_down": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polyline points="6 9 12 15 18 9"/>'
            '</svg>'
        ),
        "chevron_right": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polyline points="9 18 15 12 9 6"/>'
            '</svg>'
        ),
        "star": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="#f59e0b" '
            f'stroke="#f59e0b" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
            '</svg>'
        ),
        "user": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
            '<circle cx="12" cy="7" r="4"/>'
            '</svg>'
        ),
        "log_in": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>'
            '<polyline points="10 17 15 12 10 7"/>'
            '<line x1="15" y1="12" x2="3" y2="12"/>'
            '</svg>'
        ),
        "user_plus": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
            '<circle cx="8.5" cy="7" r="4"/>'
            '<line x1="20" y1="8" x2="20" y2="14"/>'
            '<line x1="23" y1="11" x2="17" y2="11"/>'
            '</svg>'
        ),
        "log_out": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
            '<polyline points="16 17 21 12 16 7"/>'
            '<line x1="21" y1="12" x2="9" y2="12"/>'
            '</svg>'
        ),
        "flame": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>'
            '</svg>'
        ),
        "target": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<circle cx="12" cy="12" r="10"/>'
            '<circle cx="12" cy="12" r="6"/>'
            '<circle cx="12" cy="12" r="2"/>'
            '</svg>'
        ),
        "sparkles": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>'
            '<path d="M5 3v4"/>'
            '<path d="M19 17v4"/>'
            '<path d="M3 5h4"/>'
            '<path d="M17 19h4"/>'
            '</svg>'
        ),
        "shield_check": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
            '<path d="m9 12 2 2 4-4"/>'
            '</svg>'
        ),
        "external_link": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
            '<polyline points="15 3 21 3 21 9"/>'
            '<line x1="10" y1="14" x2="21" y2="3"/>'
            '</svg>'
        ),
        "layers": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
            '<polyline points="2 17 12 22 22 17"/>'
            '<polyline points="2 12 12 17 22 12"/>'
            '</svg>'
        ),
        "trash": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polyline points="3 6 5 6 21 6"/>'
            '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
            '</svg>'
        ),
        "plus": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<line x1="12" y1="5" x2="12" y2="19"/>'
            '<line x1="5" y1="12" x2="19" y2="12"/>'
            '</svg>'
        ),
        "refresh": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polyline points="23 4 23 10 17 10"/>'
            '<polyline points="1 20 1 14 7 14"/>'
            '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
            '</svg>'
        ),
        "check": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<polyline points="20 6 9 17 4 12"/>'
            '</svg>'
        ),
        "mail": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<rect width="20" height="16" x="2" y="4" rx="2"/>'
            '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'
            '</svg>'
        ),
        "lock": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>'
            '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
            '</svg>'
        ),
        "arrow_left": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<line x1="19" y1="12" x2="5" y2="12"/>'
            '<polyline points="12 19 5 12 12 5"/>'
            '</svg>'
        ),
        "arrow_up_right": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<line x1="7" y1="17" x2="17" y2="7"/>'
            '<polyline points="7 7 17 7 17 17"/>'
            '</svg>'
        ),
        "search": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<circle cx="11" cy="11" r="8"/>'
            '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
            '</svg>'
        ),
        "bell": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>'
            '<path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>'
            '</svg>'
        ),
        "users": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
            '<circle cx="9" cy="7" r="4"/>'
            '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
            '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
            '</svg>'
        ),
        "settings": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
            '<circle cx="12" cy="12" r="3"/>'
            '</svg>'
        ),
        "help_circle": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" class="lucide {extra_class}">'
            '<circle cx="12" cy="12" r="10"/>'
            '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>'
            '<line x1="12" y1="17" x2="12.01" y2="17"/>'
            '</svg>'
        )
    }
    return svgs.get(name, f'<span class="icon-{name}"></span>')
