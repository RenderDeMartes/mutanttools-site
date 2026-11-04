// /meta-mutant/: compare sliders, the controls, expressions, phonemes, copy buttons.
(function () {
  var IMG = '/assets/img/meta-mutant/';
  var calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hero = document.querySelector('.mm-hero video');
  if (calm && hero) { hero.removeAttribute('autoplay'); hero.pause(); }

  document.querySelectorAll('[data-copy]').forEach(function (box) {
    var text = box.textContent.trim();
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
  var CONTROLS = [['jaw', 'Jaw', 0], ['smile', 'Smile', 0], ['blink', 'Blink', 0], ['look', 'Look', 4], ['brows', 'Brows', 4]];
  var face = document.getElementById('mm-face');
  var sliders = document.getElementById('mm-sliders');
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

  function pill(list, label, pressed, onClick) {
    var item = document.createElement('li');
    var button = document.createElement('button');
    button.className = 'mt-pill';
    button.type = 'button';
    button.textContent = label;
    button.setAttribute('aria-pressed', pressed ? 'true' : 'false');
    button.addEventListener('click', function () {
      list.querySelectorAll('button').forEach(function (other) { other.setAttribute('aria-pressed', 'false'); });
      button.setAttribute('aria-pressed', 'true');
      onClick();
    });
    item.appendChild(button);
    list.appendChild(item);
  }

  var expressions = document.getElementById('mm-exp');
  var expression = document.getElementById('mm-exp-img');
  ['Happy', 'Sad', 'Angry', 'Kissing', 'Yelling'].forEach(function (name, i) {
    pill(expressions, name, !i, function () {
      expression.src = IMG + 'ex_' + name.toLowerCase() + '.webp';
      expression.alt = 'The rigged head with a ' + name.toLowerCase() + ' expression';
    });
  });

  var SOUNDS = [['AA', 'father'], ['AE', 'cat'], ['AH', 'cup'], ['AO', 'law'], ['AW', 'how'], ['AY', 'my'], ['EH', 'bed'], ['ER', 'bird'], ['EY', 'day'], ['IH', 'sit'], ['IY', 'see'], ['OW', 'go'], ['OY', 'boy'], ['UH', 'book'], ['UW', 'blue'],
    ['B', 'bat'], ['CH', 'chin'], ['D', 'dog'], ['DH', 'this'], ['F', 'fan'], ['G', 'go'], ['HH', 'hat'], ['JH', 'joy'], ['K', 'kit'], ['L', 'leg'], ['M', 'man'], ['N', 'no'], ['NG', 'sing'], ['P', 'pat'], ['R', 'red'], ['S', 'sun'], ['SH', 'ship'], ['T', 'top'], ['TH', 'thin'], ['V', 'van'], ['W', 'win'], ['Y', 'yes'], ['Z', 'zoo'], ['ZH', 'vision']];
  var grid = document.getElementById('mm-ph');
  SOUNDS.forEach(function (sound, i) {
    var number = ('0' + i).slice(-2);
    var button = document.createElement('button');
    button.type = 'button';
    button.dataset.kind = i < 15 ? 'vowel' : 'consonant';
    button.setAttribute('aria-label', sound[0] + ' as in ' + sound[1]);
    button.innerHTML = '<img src="' + IMG + 'ph_' + number + '.webp" alt="" loading="lazy" width="300" height="300"><span>' + sound[0] + '</span>';
    var show = function () {
      grid.querySelectorAll('button').forEach(function (other) { other.setAttribute('aria-pressed', 'false'); });
      button.setAttribute('aria-pressed', 'true');
      var big = document.getElementById('mm-ph-img');
      big.src = IMG + 'ph_' + number + '.webp';
      big.alt = 'Mouth shape for ' + sound[0];
      document.getElementById('mm-ph-name').textContent = sound[0];
      document.getElementById('mm-ph-word').textContent = 'as in "' + sound[1] + '"';
    };
    button.addEventListener('click', show);
    grid.appendChild(button);
    if (!i) show();
  });
  var filter = document.getElementById('mm-ph-filter');
  [['All 39', ''], ['Vowels 15', 'vowel'], ['Consonants 24', 'consonant']].forEach(function (choice, i) {
    pill(filter, choice[0], !i, function () {
      grid.querySelectorAll('button').forEach(function (button) { button.hidden = !!choice[1] && button.dataset.kind !== choice[1]; });
    });
  });
})();
