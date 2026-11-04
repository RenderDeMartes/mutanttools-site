// /meta-mutant/ and /topotransfer/: compare sliders, copy buttons, the controls, expressions.
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
  var expressions = document.getElementById('mm-exp');
  if (stage && expressions) {
    ['Happy', 'Sad', 'Angry', 'Kissing', 'Yelling'].forEach(function (name, i) {
      new Image().src = IMG + 'ex_' + name.toLowerCase() + '.webp';
      var item = document.createElement('li');
      var button = document.createElement('button');
      button.className = 'mt-pill';
      button.type = 'button';
      button.textContent = name;
      button.setAttribute('aria-pressed', i ? 'false' : 'true');
      button.addEventListener('click', function () {
        expressions.querySelectorAll('button').forEach(function (other) { other.setAttribute('aria-pressed', 'false'); });
        button.setAttribute('aria-pressed', 'true');
        stage.src = IMG + 'ex_' + name.toLowerCase() + '.webp';
        stage.alt = 'The rigged head with a ' + name.toLowerCase() + ' expression';
      });
      item.appendChild(button);
      expressions.appendChild(item);
    });
  }
})();
