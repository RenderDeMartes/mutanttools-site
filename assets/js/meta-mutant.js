// /meta-mutant/ and /topotransfer/: compare sliders, copy buttons, the controls, and the stage that says typed text.
(function () {
  var IMG = '/assets/img/meta-mutant/';
  var calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hero = document.querySelector('.mm-hero video');
  if (calm && hero) { hero.removeAttribute('autoplay'); hero.pause(); }

  document.querySelectorAll('[data-copy]').forEach(function (box) {
    var text = (box.dataset.start || '') + box.textContent.trim();
    var button = document.createElement('button');
    button.className = 'mt-btn mt-btn--ghost mt-btn--sm';
    button.type = 'button';
    button.textContent = 'Copy';
    button.addEventListener('click', function () {
      var done = function () { button.textContent = 'Copied'; setTimeout(function () { button.textContent = 'Copy'; }, 1400); };
      var select = function () {
        var range = document.createRange();
        range.selectNodeContents(box.querySelector('code'));
        var selection = getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = 'Ctrl+C';
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, select);
      else select();
    });
    box.appendChild(button);
  });

  document.querySelectorAll('[data-cmp]').forEach(function (compare) {
    var input = compare.querySelector('input');
    var update = function () { compare.style.setProperty('--at', input.value + '%'); };
    input.addEventListener('input', update);
    update();
  });

  // The controls: each slider shows frames of the rig. [name, label, rest]
  var face = document.getElementById('mm-face');
  var sliders = document.getElementById('mm-sliders');
  if (face && sliders) {
    var CONTROLS = [['jaw', 'Jaw', 0], ['smile', 'Smile', 0], ['blink', 'Blink', 0], ['look', 'Look', 4], ['brows', 'Brows', 4]];
    CONTROLS.forEach(function (control) {
      for (var i = 0; i < 9; i++) { new Image().src = IMG + 's_' + control[0] + '_' + i + '.webp'; }
      var row = document.createElement('div');
      row.className = 'mm-slider';
      row.innerHTML = '<label for="mm-' + control[0] + '">' + control[1] + '</label><input id="mm-' + control[0] +
        '" type="range" min="0" max="8" step="1" value="' + control[2] + '">';
      var input = row.querySelector('input');
      var show = function () {
        sliders.querySelectorAll('.mm-slider').forEach(function (other) { other.classList.remove('is-on'); });
        row.classList.add('is-on');
        CONTROLS.forEach(function (other) { if (other !== control) document.getElementById('mm-' + other[0]).value = other[2]; });
        face.src = IMG + 's_' + control[0] + '_' + input.value + '.webp';
        face.alt = 'The rigged head with ' + control[1] + ' at ' + input.value + ' of 8';
      };
      input.addEventListener('input', show);
      input.addEventListener('focus', show);
      sliders.appendChild(row);
    });
  }

  var stage = document.getElementById('mm-stage');
  if (!stage) return;

  // ------------------------------------------------------------ text to sounds
  // Common words as written in ARPAbet, then spelling rules: an approximation of English, for a mouth to follow.
  var WORDS = {
    the: 'DH AH', a: 'AH', an: 'AE N', and: 'AE N D', i: 'AY', im: 'AY M', am: 'AE M', you: 'Y UW', your: 'Y AO R', to: 'T UW', too: 'T UW', do: 'D UW', of: 'AH V',
    is: 'IH Z', are: 'AA R', was: 'W AA Z', be: 'B IY', he: 'HH IY', she: 'SH IY', we: 'W IY', me: 'M IY', my: 'M AY', by: 'B AY', this: 'DH IH S', that: 'DH AE T',
    these: 'DH IY Z', those: 'DH OW Z', they: 'DH EY', there: 'DH EH R', their: 'DH EH R', then: 'DH EH N', them: 'DH EH M', what: 'W AH T', who: 'HH UW', how: 'HH AW', now: 'N AW',
    know: 'N OW', one: 'W AH N', two: 'T UW', three: 'TH R IY', four: 'F AO R', five: 'F AY V', six: 'S IH K S', seven: 'S EH V AH N', eight: 'EY T', nine: 'N AY N', ten: 'T EH N', zero: 'Z IY R OW',
    hello: 'HH AH L OW', hi: 'HH AY', good: 'G UH D', new: 'N UW', face: 'F EY S', meta: 'M EH T AH', mutant: 'M Y UW T AH N T', maya: 'M AY AH', rig: 'R IH G', have: 'HH AE V',
    said: 'S EH D', says: 'S EH Z', come: 'K AH M', some: 'S AH M', love: 'L AH V', give: 'G IH V', live: 'L IH V', people: 'P IY P AH L', world: 'W ER L D', would: 'W UH D', could: 'K UH D', should: 'SH UH D',
    because: 'B IH K AO Z', thanks: 'TH AE NG K S', thank: 'TH AE NG K', yes: 'Y EH S', no: 'N OW', go: 'G OW', so: 'S OW', very: 'V EH R IY', great: 'G R EY T', animation: 'AE N AH M EY SH AH N',
    character: 'K EH R AH K T ER', tutorial: 'T UW T AO R IY AH L', with: 'W IH DH', from: 'F R AH M', for: 'F AO R', not: 'N AA T', can: 'K AE N', will: 'W IH L', all: 'AO L', want: 'W AA N T',
    time: 'T AY M', name: 'N EY M', here: 'HH IY R', where: 'W EH R', when: 'W EH N', why: 'W AY', like: 'L AY K', make: 'M EY K', head: 'HH EH D', talk: 'T AO K', walk: 'W AO K', day: 'D EY', see: 'S IY'
  };
  var RULES = [['tion', 'SH AH N'], ['sion', 'ZH AH N'], ['ture', 'CH ER'], ['eigh', 'EY'], ['igh', 'AY'], ['tch', 'CH'], ['dge', 'JH'], ['ch', 'CH'], ['sh', 'SH'], ['th', 'TH'], ['ph', 'F'], ['wh', 'W'],
    ['ck', 'K'], ['ng', 'NG'], ['qu', 'K W'], ['ee', 'IY'], ['ea', 'IY'], ['ie', 'IY'], ['oo', 'UW'], ['ou', 'AW'], ['ow', 'OW'], ['oi', 'OY'], ['oy', 'OY'], ['ai', 'EY'], ['ay', 'EY'], ['au', 'AO'],
    ['aw', 'AO'], ['oa', 'OW'], ['ew', 'UW'], ['ey', 'IY'], ['ar', 'AA R'], ['er', 'ER'], ['ir', 'ER'], ['ur', 'ER'], ['or', 'AO R']];
  var LETTERS = { a: 'AE', b: 'B', d: 'D', e: 'EH', f: 'F', g: 'G', h: 'HH', i: 'IH', j: 'JH', k: 'K', l: 'L', m: 'M', n: 'N', o: 'AA', p: 'P', r: 'R', s: 'S', t: 'T', u: 'AH', v: 'V', w: 'W', x: 'K S', z: 'Z' };
  var LONG = { a: 'EY', e: 'IY', i: 'AY', o: 'OW', u: 'UW' };

  function byRules(word) {
    var out = [];
    var w = word.replace(/^kn/, 'n').replace(/^wr/, 'r').replace(/^gn/, 'n').replace(/([bcdfgklmnprstz])\1/g, '$1');
    if (!/[aeiouy]/.test(w)) return w.split('').map(function (c) { return LETTERS[c] || (c === 'c' || c === 'q' ? 'K' : ''); }).join(' ').trim().split(/\s+/).filter(Boolean);
    var i = 0;
    while (i < w.length) {
      var hit = null;
      for (var r = 0; r < RULES.length; r++) {
        if (w.substr(i, RULES[r][0].length) === RULES[r][0]) { hit = RULES[r]; break; }
      }
      if (hit) { out.push(hit[1]); i += hit[0].length; continue; }
      var c = w[i], rest = w.slice(i + 1);
      if ('aeiou'.indexOf(c) >= 0 && /^[bcdfgklmnprstvz]e$/.test(rest)) { out.push(LONG[c]); i++; continue; }  // the e of "made"
      if (c === 'e' && i === w.length - 1 && i > 0) { i++; continue; }  // silent
      if (c === 'e' && rest === 'd' && i > 1) { i++; continue; }  // walked
      if (c === 's' && i === w.length - 1 && i > 0 && 'aeiou'.indexOf(w[i - 1]) >= 0) { out.push('Z'); i++; continue; }
      if (c === 'c') { out.push(/^[eiy]/.test(rest) ? 'S' : 'K'); i++; continue; }
      if (c === 'q') { out.push('K'); i++; continue; }
      if (c === 'y') { out.push(i === 0 ? 'Y' : i === w.length - 1 ? (/[aeiou]/.test(w.slice(0, i)) ? 'IY' : 'AY') : 'IH'); i++; continue; }
      if (LETTERS[c]) out.push(LETTERS[c]);
      i++;
    }
    return out.join(' ').split(/\s+/).filter(Boolean);
  }

  var DIGITS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];

  /** Text -> [{word, sounds}], with pauses as words without sounds. */
  function toSounds(text) {
    var out = [];
    (text.toLowerCase().match(/[a-z']+|\d|[.,;:!?]/g) || []).forEach(function (token) {
      if (/^[.,;:!?]$/.test(token)) { out.push({ word: token, sounds: [] }); return; }
      var word = /^\d$/.test(token) ? DIGITS[+token] : token.replace(/'/g, '');
      if (!word) return;
      out.push({ word: token, sounds: WORDS[word] ? WORDS[word].split(' ') : byRules(word) });
    });
    return out;
  }
  window.mmSounds = toSounds;  // handy in the console, and for testing

  // ---------------------------------------------------------------- the stage
  // Each sound is one or two mouth shapes, rendered from the rig, as is the shape halfway between any two.
  var NAMES = ['rest', 'AA', 'AE', 'AH', 'AO', 'EH', 'ER', 'IH', 'IY', 'UH', 'UW', 'MBP', 'M', 'FV', 'TH', 'TDN', 'L', 'KG', 'SZ', 'SH', 'R', 'W', 'Y', 'HH'];
  var SHAPES = { AA: ['AA'], AE: ['AE'], AH: ['AH'], AO: ['AO'], AW: ['AA', 'UW'], AY: ['AA', 'IY'], EH: ['EH'], ER: ['ER'], EY: ['EH', 'IY'], IH: ['IH'], IY: ['IY'], OW: ['AO', 'UW'], OY: ['AO', 'IY'], UH: ['UH'], UW: ['UW'],
    B: ['MBP'], CH: ['SH'], D: ['TDN'], DH: ['TH'], F: ['FV'], G: ['KG'], HH: ['HH'], JH: ['SH'], K: ['KG'], L: ['L'], M: ['M'], N: ['TDN'], NG: ['KG'], P: ['MBP'], R: ['R'], S: ['SZ'], SH: ['SH'], T: ['TDN'], TH: ['TH'], V: ['FV'], W: ['W'], Y: ['Y'], Z: ['SZ'], ZH: ['SH'] };
  var VOWELS = /^(AA|AE|AH|AO|AW|AY|EH|ER|EY|IH|IY|OW|OY|UH|UW)$/;
  var FPS = 24;
  var HOLD_VOWEL = 4, HOLD_CONSONANT = 2, HOLD_CLOSED = 3, HOLD_GLIDE = 2, PAUSE = 8;

  function frameOf(a, b) {
    if (a === b) return 'v_' + a;
    return NAMES.indexOf(a) < NAMES.indexOf(b) ? 'm_' + a + '_' + b : 'm_' + b + '_' + a;
  }

  /** The words as a list of frames: {src, token}, token being the index of the chip it belongs to. */
  function timeline(words) {
    var frames = [], tokens = [], last = 'rest';
    var add = function (shape, hold, token) {
      if (shape !== last) frames.push({ src: frameOf(last, shape), token: token });
      for (var i = 0; i < hold; i++) frames.push({ src: 'v_' + shape, token: token });
      last = shape;
    };
    add('rest', 3, -1);
    words.forEach(function (word) {
      if (!word.sounds.length) { add('rest', PAUSE, -1); return; }
      word.sounds.forEach(function (sound) {
        var shapes = SHAPES[sound];
        if (!shapes) return;
        var token = tokens.length;
        tokens.push({ sound: sound, word: word.word });
        if (shapes.length === 2) { add(shapes[0], HOLD_GLIDE + 1, token); add(shapes[1], HOLD_GLIDE, token); return; }
        var closed = shapes[0] === 'MBP' || shapes[0] === 'M';
        add(shapes[0], VOWELS.test(sound) ? HOLD_VOWEL : closed ? HOLD_CLOSED : HOLD_CONSONANT, token);
      });
    });
    add('rest', 8, -1);
    return { frames: frames, tokens: tokens };
  }

  var input = document.getElementById('mm-say');
  var play = document.getElementById('mm-play');
  var scrub = document.getElementById('mm-scrub');
  var chips = document.getElementById('mm-chips');
  var loaded = {}, line = null, at = 0, playing = false, started = 0, startFrame = 0, ticket = 0;

  function load(name) {
    if (!loaded[name]) {
      loaded[name] = new Promise(function (resolve) {
        var image = new Image();
        image.onload = image.onerror = function () { resolve(image); };
        image.src = IMG + name + '.webp';
      });
    }
    return loaded[name];
  }

  function draw(index) {
    at = Math.max(0, Math.min(line.frames.length - 1, index));
    var frame = line.frames[at];
    stage.src = IMG + frame.src + '.webp';
    stage.alt = 'The rigged head saying the text';
    scrub.value = at;
    chips.querySelectorAll('button').forEach(function (chip, i) { chip.classList.toggle('is-on', i === frame.token); });
  }

  function stop() { playing = false; play.textContent = 'Play'; }

  function tick(now) {
    if (!playing) return;
    var index = startFrame + Math.floor((now - started) / 1000 * FPS);
    if (index >= line.frames.length) { draw(line.frames.length - 1); stop(); return; }
    if (index !== at) draw(index);
    requestAnimationFrame(tick);
  }

  function start() {
    var mine = ++ticket;
    play.textContent = 'Loading';
    Promise.all(line.frames.map(function (frame) { return load(frame.src); })).then(function () {
      if (mine !== ticket) return;
      if (at >= line.frames.length - 1) at = 0;
      playing = true;
      play.textContent = 'Pause';
      draw(at);
      startFrame = at;
      started = performance.now();
      requestAnimationFrame(tick);
    });
  }

  function setLine(words) {
    ticket++;
    stop();
    line = timeline(words);
    scrub.max = line.frames.length - 1;
    chips.innerHTML = '';
    line.tokens.forEach(function (token, number) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.textContent = token.sound;
      chip.title = token.word;
      chip.addEventListener('click', function () {
        ticket++;
        stop();
        for (var i = line.frames.length - 1; i >= 0; i--) {
          if (line.frames[i].token === number) { load(line.frames[i].src); draw(i); return; }
        }
      });
      chips.appendChild(chip);
    });
    draw(0);
  }

  var waiting = 0;
  input.addEventListener('input', function () {
    clearTimeout(waiting);
    waiting = setTimeout(function () { setLine(toSounds(input.value)); }, 200);
  });
  input.form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearTimeout(waiting);
    setLine(toSounds(input.value));
    start();
  });
  play.addEventListener('click', function () {
    if (playing) { ticket++; stop(); return; }
    start();
  });
  scrub.addEventListener('input', function () {
    ticket++;
    stop();
    draw(+scrub.value);
  });

  function pill(list, label, onClick) {
    var item = document.createElement('li');
    var button = document.createElement('button');
    button.className = 'mt-pill';
    button.type = 'button';
    button.textContent = label;
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', function () {
      list.querySelectorAll('button').forEach(function (other) { other.setAttribute('aria-pressed', 'false'); });
      button.setAttribute('aria-pressed', 'true');
      onClick();
    });
    item.appendChild(button);
    list.appendChild(item);
  }

  var expressions = document.getElementById('mm-exp');
  ['Happy', 'Sad', 'Angry', 'Kissing', 'Yelling'].forEach(function (name) {
    pill(expressions, name, function () {
      ticket++;
      stop();
      stage.src = IMG + 'ex_' + name.toLowerCase() + '.webp';
      stage.alt = 'The rigged head with a ' + name.toLowerCase() + ' expression';
    });
  });

  var SOUNDS = [['AA', 'father'], ['AE', 'cat'], ['AH', 'cup'], ['AO', 'law'], ['AW', 'how'], ['AY', 'my'], ['EH', 'bed'], ['ER', 'bird'], ['EY', 'day'], ['IH', 'sit'], ['IY', 'see'], ['OW', 'go'], ['OY', 'boy'], ['UH', 'book'], ['UW', 'blue'],
    ['B', 'bat'], ['CH', 'chin'], ['D', 'dog'], ['DH', 'this'], ['F', 'fan'], ['G', 'go'], ['HH', 'hat'], ['JH', 'joy'], ['K', 'kit'], ['L', 'leg'], ['M', 'man'], ['N', 'no'], ['NG', 'sing'], ['P', 'pat'], ['R', 'red'], ['S', 'sun'], ['SH', 'ship'], ['T', 'top'], ['TH', 'thin'], ['V', 'van'], ['W', 'win'], ['Y', 'yes'], ['Z', 'zoo'], ['ZH', 'vision']];
  var soundList = document.getElementById('mm-sounds');
  SOUNDS.forEach(function (sound) {
    pill(soundList, sound[0] + ' ' + sound[1], function () {
      setLine([{ word: sound[1], sounds: [sound[0]] }]);
      start();
    });
  });

  setLine(toSounds(input.value));
})();
