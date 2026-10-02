# -*- coding: utf-8 -*-
"""Builds /rigger/, /learn/, /free-assets/ and /contact/.

These four were WordPress pages with their own one-off block styles - grey
cards, thin uppercase titles - that matched nothing else on the site. They are
now written from the same components as the docs (mt_md: hero, card, button,
cta), so every page except the homepage shares one look. The copy is carried
over from the WordPress versions.
"""
import mt_md as m

GH = "https://github.com/RenderDeMartes/Mutant_Tools"
LINKEDIN = "https://www.linkedin.com/in/esteban-rodriguez-488a68147/"

# (kicker, title, description, YouTube id). An id starting "PL" is a playlist,
# anything else a single video.
TUTORIALS = [
    ("Getting started", "Mutant Tools &amp; Asset Browser &ndash; Installation Guide",
     "Install Mutant Tools, configure the Asset Browser, and prepare your Maya environment.",
     "PLYMDeEG84lPE-UA-D6i4aS_XmmQUXys-a"),
    ("Practical rigging", "Rigging a Prop with Mutant Tools &ndash; Step by Step",
     "A full prop rig built using Mutant Tools blocks in a clean, repeatable workflow.",
     "PLYMDeEG84lPGiZymg5FpDA9_kbaUo1eC6"),
    ("Core system", "Mutant Tools Rigging System &ndash; Understanding All Blocks",
     "A complete overview of the Mutant Tools rigging system and every available block.",
     "PLYMDeEG84lPEwyeJM4Ez8duIS4wYzXenH"),
    ("Beginner series", "Character Rigging 101 &ndash; Mutant Tools Biped",
     "A complete beginner-friendly guide to character rigging, covering the full biped "
     "workflow using Mutant Tools.",
     "PLYMDeEG84lPHqqycBQ1bW52B74H82FetZ"),
    ("Advanced rigging", "Quadruped Rigging in Maya | Mutant Tools Tutorial",
     "A complete step-by-step guide to rigging quadruped characters using the Mutant Tools "
     "workflow in Maya.",
     "PLYMDeEG84lPG2O4freXQ66X7TehlTsK8m"),
    ("Mocap", "Mixamo Mocap in Mutant Tools",
     "Bring Mixamo motion capture onto a Mutant Tools rig with HumanIK retargeting.",
     "1y6Znuj1zs0"),
]

# (kicker, title, author, image, download link)
ASSETS = [
    ("Character", "Loris Character Rig", "Yang Xiao",
     "https://public-files.gumroad.com/id17z7pwrhhked21s75kjirjjbc8",
     "https://xiaoy96.gumroad.com/l/mteexk"),
]


def _open():
    return '<div class="mt-wrap mt-section">'


def _close():
    return '</div>'


def rigger(stats):
    b = [m.hero("Tutorials", "Rigging with Mutant Tools",
                "Practical learning paths focused on real production workflows using Mutant Tools."),
         _open(), '<div class="mt-grid mt-grid--3">']
    for kicker, title, desc, yid in TUTORIALS:
        if yid.startswith("PL"):
            embed = "videoseries?list=%s" % yid
            link = m.btn("Open playlist", "https://www.youtube.com/playlist?list=%s" % yid, ghost=True)
        else:
            embed = yid
            link = m.btn("Watch on YouTube", "https://www.youtube.com/watch?v=%s" % yid, ghost=True)
        video = ('<iframe src="https://www.youtube.com/embed/%s" title="%s" '
                 'loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" '
                 'allowfullscreen></iframe>' % (embed, title))
        b.append(m.media_card(title, desc, video, kicker=kicker, button=link))
    b.append('</div>')
    b.append(m.cta("Prefer to read?",
                   "Every one of the %d blocks is documented with its options and the command the "
                   "builder runs." % stats["blocks"],
                   m.btn("Block catalogue", "/wiki/blocks/"),
                   m.btn("How the auto rigger works", "/maya-auto-rigger/", ghost=True)))
    b.append(_close())
    return "".join(b)


def learn(stats):
    def img(src, alt):
        return '<img src="%s" alt="%s" loading="lazy">' % (src, alt)

    b = [m.hero("Learn", "Learn Mutant Tools",
                "Tutorials, block-based workflows and production examples for rigging in Maya "
                "with Mutant Tools."),
         _open(), '<div class="mt-grid mt-grid--2">',
         m.media_card("Rigger",
                      "Learn character rigging from start to finish using Mutant Tools blocks "
                      "&ndash; real production workflows, step by step.",
                      img("/assets/img/santa_render.png", "A character rigged with Mutant Tools"),
                      kicker="Rigging path", href="/rigger/"),
         m.media_card("Developer",
                      "Explore the Python wiki, MT command library, and learn how to build custom "
                      "blocks and extend Mutant Tools.",
                      img("/assets/img/code.png", "Mutant Tools Python source in an editor"),
                      kicker="Technical path", href="/developer/"),
         '</div>', _close()]
    return "".join(b)


def free_assets(stats):
    b = [m.hero("Community", "Free rigging assets",
                "Free rigs for animation practice, testing, and learning real production workflows."),
         _open(), '<div class="mt-grid mt-grid--3">']
    for kicker, title, author, image, link in ASSETS:
        b.append(m.media_card(title, "by %s" % author,
                              '<img src="%s" alt="%s" loading="lazy">' % (image, title),
                              kicker=kicker, button=m.btn("Download", link, ghost=True)))
    b.append('</div>')
    b.append(_close())
    return "".join(b)


def contact(stats):
    # The address is assembled in the browser by assets/js/site.js, so it never
    # appears in the HTML for scrapers to collect.
    mail = ('<button class="mt-btn" type="button" data-mail data-u="info" '
            'data-d="renderdemartes.com" data-s="Mutant Tools">Email me</button>')
    return m.hero("Get in touch", "Contact",
                  "Questions about Mutant Tools, studio services, custom rigging or pipeline "
                  "development &mdash; the fastest way to reach me is email.",
                  m.actions(mail, m.btn("LinkedIn", LINKEDIN, ghost=True)))


# (slug, builder, title, description, nav href to mark current)
PAGES = [
    ("rigger", rigger, "For Riggers — Mutant Tools",
     "Mutant Tools for riggers: modular blocks, guide placement, rebuilds that keep controllers "
     "and skins, and a workflow built for real deadlines.", "/rigger/"),
    ("learn", learn, "Learn — Mutant Tools",
     "Tutorials, block-based workflows and production examples for rigging in Maya with "
     "Mutant Tools.", ""),
    ("free-assets", free_assets, "Free Assets — Mutant Tools",
     "Free rigs, tools and assets from Mutant Tools for riggers and animators.", ""),
    ("contact", contact, "Contact — Mutant Tools",
     "Get in touch about Mutant Tools, studio services, custom rigging and pipeline "
     "development.", ""),
]
