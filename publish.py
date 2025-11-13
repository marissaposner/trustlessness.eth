#!/usr/bin/python3
import os, sys
from string import Template

HEADER_TEMPLATE = Template("""

<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<base href="${base}">

<link rel="stylesheet" type="text/css" href="css/common-vendor.b8ecfc406ac0b5f77a26.css">
<link rel="stylesheet" type="text/css" href="css/font-vendor.b86e2bf451b246b1a88e.css">
<link rel="stylesheet" type="text/css" href="css/fretboard.f32f2a8d5293869f0195.css">
<link rel="stylesheet" type="text/css" href="css/pretty.0ae3265014f89d9850bf.css">
<link rel="stylesheet" type="text/css" href="css/pretty-vendor.83ac49e057c3eac4fce3.css">
<link rel="stylesheet" type="text/css" href="css/misc.css">
<link rel="stylesheet" type="text/css" href="css/main.css">

<script type="text/javascript" id="MathJax-script" async
  src="scripts/mathjax.js">
</script>

<style>
@font-face {
    font-family: MJXc-TeX-math-Iw;
    src: url("https://assets.hackmd.io/build/MathJax/fonts/HTML-CSS/TeX/woff/MathJax_Main-Regular.woff")
}
@font-face {
    font-family: MJXZERO;
    src: url("https://assets.hackmd.io/build/MathJax/fonts/HTML-CSS/TeX/woff/MathJax_Main-Regular.woff")
}
@font-face {
    font-family: MJXTEX;
    src: url("https://assets.hackmd.io/build/MathJax/fonts/HTML-CSS/TeX/woff/MathJax_Main-Regular.woff")
}

.math { font-family: MJXc-TeX-math-Iw }
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1c1c1c;
        color: white;
    }
    .markdown-body table tr {
        background-color: #1c1c1c;
    }
    .markdown-body table tr:nth-child(2n) {
        background-color: black;
    }
}
html.light body {
    background-color: #fff;
    color: #333;
}
</style>

<div id="doc" class="container-fluid markdown-body comment-enabled" data-hard-breaks="true">

""")

FOOTER = """ </div> """

TOGGLE_TEMPLATE_TEMPLATE = Template("""
<div class="color-toggle" id="color-mode-switch">
  <svg xmlns="http://www.w3.org/2000/svg" class="toggle-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
  <input type="checkbox" id="switch" />
  <label for="switch">Dark Mode Toggle</label>
  <svg xmlns="http://www.w3.org/2000/svg" class="toggle-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
  </svg>
</div>

<script>
  window.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const toggle = document.querySelector('#color-mode-switch input[type="checkbox"]');
    if (!toggle) return;

    const applyScheme = (mode) => {
      if (mode === 'dark') {
        root.classList.add('dark');
        root.classList.remove('light');
      } else {
        root.classList.add('light');
        root.classList.remove('dark');
      }
      localStorage.setItem('colorScheme', mode);
    };

    const stored = localStorage.getItem('colorScheme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialMode = stored || (prefersDark ? 'dark' : 'light');
    applyScheme(initialMode);
    toggle.checked = initialMode === 'dark';

    toggle.addEventListener('change', () => {
      applyScheme(toggle.checked ? 'dark' : 'light');
    });
  });
</script>

""")

def render_toggle(prefix):
    return TOGGLE_TEMPLATE_TEMPLATE.substitute(prefix=prefix)

HERO_TEMPLATE = Template("""
<div class="site-landing">
  <img class="site-hero-logo" src="${icon}" alt="${title} logo">
  <h1 class="site-title-heading">${title}</h1>
  <p class="site-tagline">${tagline}</p>
</div>
""")

TAGLINE = "trustlessness.eth explores the values that make Ethereum unique: credible neutrality, self-custody, and verifiable execution. This is a space for people who still believe that trustlessness isn’t just a feature; it’s the point."

TOC_HEADER = """

<ul class="post-list">

"""

TOC_FOOTER = """ </ul> """

TOC_ITEM_TEMPLATE = """

<li>
    <span class="post-meta">{}</span>
    <h3>
      <a class="post-link" href="{}">{}</a>
    </h3>
</li>

"""

TWITTER_CARD_TEMPLATE = """
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:image" content="{image}" />
"""

def extract_metadata(fil, filename=None):
    metadata = {}
    if filename:
        assert filename[-3:] == '.md'
        metadata["filename"] = filename[:-3]+'.html'
    while 1:
        line = fil.readline()
        if line and line[0] == '[' and ']' in line:
            key = line[1:line.find(']')]
            value_start = line.index('(')+1
            value_end = line.index(')')
            metadata[key] = line[value_start:value_end]
        else:
            break
    return metadata


def metadata_to_path(metadata):
    return os.path.join(metadata['category'].lower(), metadata['date'], metadata['filename'])


def make_twitter_card(title, icon_path):
    return TWITTER_CARD_TEMPLATE.format(title=title, image=icon_path)


def defancify(text):
    return text \
        .replace("’", "'") \
        .replace('“', '"') \
        .replace('”', '"') \
        .replace('…', '...') \


def make_toc_item(metadata):
    year, month, day = metadata['date'].split('/')
    month = 'JanFebMarAprMayJunJulAugSepOctNovDec'[int(month)*3-3:][:3]
    link = metadata_to_path(metadata)
    return TOC_ITEM_TEMPLATE.format(year+' '+month+' '+day, link, metadata['title'])


def compute_base(path):
    depth = path.count('/')
    base = ('../' * depth) or './'
    return base

if __name__ == '__main__':
    # Get blog config
    global_config = extract_metadata(open('config.md'))

    # Special case: '--sync' option
    if sys.argv[1:] == ['--sync']:
        os.system('rsync -av site/. {}:{}'.format(global_config['server'], global_config['website_root']))
        os.system('rsync -av images {}:{}'.format(global_config['server'], global_config['website_root']))
        sys.exit()

    # Normal case: process each provided file
    for file_location in sys.argv[1:]:
        filename = os.path.split(file_location)[1]
        print("Processing file: {}".format(filename))
        
        # Extract path
        file_data = open(file_location).read()
        metadata = extract_metadata(open(file_location), filename)
        path = metadata_to_path(metadata)
        print("Path selected: {}".format(path))
        
        # Make sure target directory exists
        truncated_path = os.path.split(path)[0]
        os.system('mkdir -p {}'.format(os.path.join('site', truncated_path)))
        
        # Generate the html file
        out_location = os.path.join('site', path)
        options = metadata.get('pandoc', '')
        
        os.system('pandoc -o /tmp/temp_output.html {} {}'.format(file_location, options))
        base = compute_base(path)
        header = HEADER_TEMPLATE.substitute(base=base)
        icon_path = global_config['icon']
        total_file_contents = (
            header +
            make_twitter_card(metadata['title'], icon_path) +
            render_toggle(base) +
            defancify(open('/tmp/temp_output.html').read()) +
            FOOTER
        )
    
        # Put it in the desired location
        open(out_location, 'w').write(total_file_contents)

    # Reset ToC
    metadatas = []
    for filename in os.listdir('posts'):
        if filename[-4:-1] != '.sw':
            metadatas.append(extract_metadata(open(os.path.join('posts', filename)), filename))

    sorted_metadatas = sorted(metadatas, key=lambda x: x['date'], reverse=True)
    toc_items = [make_toc_item(metadata) for metadata in sorted_metadatas]

    index_base = compute_base('index.html')
    header_index = HEADER_TEMPLATE.substitute(base=index_base)
    icon_path_index = global_config['icon']
    toc = (
        header_index +
        make_twitter_card(global_config['title'], icon_path_index) +
        render_toggle(index_base) +
        HERO_TEMPLATE.substitute(title=global_config['title'], icon=global_config['icon'], tagline=TAGLINE) +
        TOC_HEADER +
        ''.join(toc_items) +
        TOC_FOOTER
    )

    open('site/index.html', 'w').write(toc)
