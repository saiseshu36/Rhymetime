const cards = [...document.querySelectorAll('.song-card')];
const titleEl = document.getElementById('playerTitle');
const subtitleEl = document.getElementById('playerSubtitle');
const emojiEl = document.getElementById('recordEmoji');
const lyricsEl = document.getElementById('lyrics');
const playBtn = document.getElementById('playBtn');
const favoriteBtn = document.getElementById('favorite');
const progressFill = document.getElementById('progressFill');
const elapsedEl = document.getElementById('elapsed');
const durationEl = document.getElementById('duration');
const toast = document.getElementById('toast');
const rhymeAudio = document.getElementById('rhymeAudio');
const rhymeVideo = document.getElementById('rhymeVideo');
let activeMedia = rhymeAudio;
let activeIndex = 0;
let currentRhyme = null;
let timer = null;
let toastTimer = null;
let playing = false;
let musicContext = null;
let musicTimer = null;
let musicStep = 0;
let musicEnabled = false;
const musicToggle = document.getElementById('musicToggle');

const fallback = [
  { title: 'A gentle bedtime favorite', lyrics: 'Twinkle, twinkle, little star,\nHow I wonder what you are!\nUp above the world so high,\nLike a diamond in the sky.\nTwinkle, twinkle, little star,\nHow I wonder what you are!' }
];

const rhymeMelodies = {
  twinkle: [261.63, 261.63, 392.00, 392.00, 440.00, 440.00, 392.00, 349.23, 349.23, 329.63, 329.63, 293.66, 293.66, 261.63],
  wheels: [392.00, 392.00, 392.00, 440.00, 523.25, 523.25, 440.00, 523.25, 523.25, 440.00, 440.00, 392.00],
  mary: [329.63, 293.66, 261.63, 293.66, 329.63, 329.63, 329.63, 293.66, 293.66, 293.66, 329.63, 392.00, 392.00],
  oldmacdonald: [392.00, 392.00, 392.00, 293.66, 329.63, 329.63, 329.63, 392.00, 392.00, 392.00, 392.00],
  rowboat: [261.63, 261.63, 261.63, 293.66, 329.63, 329.63, 293.66, 329.63, 392.00, 392.00, 329.63, 293.66, 261.63],
  itsybitsy: [261.63, 329.63, 392.00, 392.00, 440.00, 440.00, 392.00, 349.23, 329.63, 293.66, 261.63]
};
const rhymeNotes = {
  twinkle: [1.05, 1.05, 1.25, 1.25, 1.32, 1.32],
  wheels: [1.12, 1.12, 1.12, 1.18, 1.26, 1.26, 1.18, 1.26],
  mary: [1.26, 1.18, 1.08, 1.18, 1.26, 1.26, 1.26, 1.18],
  oldmacdonald: [1.14, 1.14, 1.14, 1.02, 1.08, 1.08, 1.08, 1.14],
  rowboat: [1.04, 1.04, 1.04, 1.10],
  itsybitsy: [1.05, 1.16, 1.25, 1.25],
  default: [1.05, 1.15, 1.25, 1.15]
};
function playMusicNote(frequency, startAt, duration, volume, type = 'triangle') {
  const oscillator = musicContext.createOscillator();
  const gain = musicContext.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, startAt);
  gain.gain.setValueAtTime(0.0001, startAt);
  gain.gain.exponentialRampToValueAtTime(volume, startAt + 0.025);
  gain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);
  oscillator.connect(gain);
  gain.connect(musicContext.destination);
  oscillator.start(startAt);
  oscillator.stop(startAt + duration + 0.03);
}
function updateMusicButton() {
  musicToggle.textContent = musicEnabled ? '♫ MUSIC ON' : '♫ MUSIC OFF';
  musicToggle.setAttribute('aria-pressed', String(musicEnabled));
  document.body.classList.toggle('music-active', musicEnabled);
}
async function toggleMusic() {
  if (musicEnabled) {
    musicEnabled = false;
    clearInterval(musicTimer);
    musicTimer = null;
    updateMusicButton();
    return;
  }
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) { showToast('Music is not supported in this browser.'); return; }
  try {
    musicContext ||= new AudioContextClass();
    await musicContext.resume();
    musicEnabled = true;
    updateMusicButton();
    const melody = () => rhymeMelodies[currentRhyme?.id] || rhymeMelodies.twinkle;
    const beat = 0.34;
    const playBeat = () => {
      if (!musicEnabled) return;
      const now = musicContext.currentTime + 0.03;
      const notes = melody();
      playMusicNote(notes[musicStep % notes.length], now, beat * 0.82, 0.035);
      if (musicStep % 4 === 0) playMusicNote(notes[musicStep % notes.length] / 2, now, beat * 1.5, 0.018, 'sine');
      musicStep++;
    };
    playBeat();
    musicTimer = setInterval(playBeat, beat * 1000);
  } catch (error) {
    musicEnabled = false;
    updateMusicButton();
    showToast('Could not start music. Tap to try again.');
  }
}
function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
}
function stopSpeech() {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  clearInterval(timer);
  timer = null;
  playing = false;
  document.body.classList.remove('is-playing');
  rhymeAudio.pause();
  rhymeVideo.pause();
  if (rhymeAudio.currentSrc) rhymeAudio.currentTime = 0;
  if (rhymeVideo.currentSrc) rhymeVideo.currentTime = 0;
  playBtn.textContent = '\u25B6';
  playBtn.setAttribute('aria-label', 'Sing this rhyme');
}
function formatTime(seconds) {
  return `0:${String(Math.floor(seconds)).padStart(2, '0')}`;
}
function render(rhyme) {
  stopSpeech();
  currentRhyme = rhyme;
  rhymeAudio.removeAttribute('src');
  rhymeVideo.removeAttribute('src');
  activeMedia = rhyme.vocal_video ? rhymeVideo : rhymeAudio;
  if (rhyme.audio_url) {
    const audioUrl = new URL(rhyme.audio_url, window.location.href);
    audioUrl.searchParams.set('v', String(Date.now()));
    activeMedia.src = audioUrl.toString();
    activeMedia.load();
  }
  titleEl.textContent = rhyme.title;
  subtitleEl.textContent = rhyme.vocal_track ? (rhyme.vocal_label || 'Human singing') : (rhyme.audio_url ? 'Instrumental tune - sing along!' : 'Instrumental track not added yet');
  const creditEl = document.getElementById('audioCredit');
  creditEl.replaceChildren();
  creditEl.hidden = !rhyme.vocal_track || !rhyme.vocal_source;
  if (rhyme.vocal_track && rhyme.vocal_source) {
    const creditLink = document.createElement('a');
    creditLink.href = rhyme.vocal_source;
    creditLink.target = '_blank';
    creditLink.rel = 'noopener noreferrer';
    creditLink.textContent = rhyme.vocal_credit || 'Human vocal recording source';
    creditEl.append(creditLink);
  }
  emojiEl.textContent = rhyme.emoji;
  lyricsEl.replaceChildren(...rhyme.lyrics.split(/\r?\n/).map(line => {
    const lineElement = document.createElement('span');
    lineElement.className = 'lyric-line';
    lineElement.textContent = line;
    return lineElement;
  }));
  const words = rhyme.lyrics.split(/\s+/).length;
  durationEl.textContent = formatTime(Math.max(10, Math.round(words / 2.3)));
  elapsedEl.textContent = '0:00';
  progressFill.style.width = '0%';
  stopSpeech();
}
async function selectCard(index) {
  activeIndex = (index + cards.length) % cards.length;
  cards.forEach((card, i) => {
    card.classList.toggle('selected', i === activeIndex);
    card.setAttribute('aria-pressed', String(i === activeIndex));
  });
  const card = cards[activeIndex];
  try {
    const response = await fetch('/api/play', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: card.dataset.query })
    });
    if (!response.ok) throw new Error('Could not load this rhyme');
    render(await response.json());
  } catch (error) {
    const local = fallback[0];
    render({ title: card.dataset.query, description: 'A lovely little song', emoji: card.querySelector('.card-emoji').textContent, lyrics: local.lyrics });
    showToast('Rhyme loaded — start singing!');
  }
}
function speak() {
  if (!currentRhyme) return;
  if (playing) { stopSpeech(); return; }
  if (!currentRhyme.audio_url) {
    showToast('This rhyme?s instrumental track is not available yet.');
    return;
  }
  if (musicEnabled) {
    musicEnabled = false;
    clearInterval(musicTimer);
    musicTimer = null;
    updateMusicButton();
  }
  activeMedia.currentTime = 0;
  activeMedia.play().catch(() => showToast('Could not play this track. Check the audio output and file.'));
}
function onMediaPlay() {
  playing = true;
  document.body.classList.add('is-playing');
  playBtn.textContent = '\u23F8';
  playBtn.setAttribute('aria-label', 'Stop rhyme');
}
function onMediaTimeUpdate(media) {
  if (media !== activeMedia || !Number.isFinite(media.duration)) return;
  elapsedEl.textContent = formatTime(media.currentTime);
  durationEl.textContent = formatTime(media.duration);
  progressFill.style.width = `${media.currentTime / media.duration * 100}%`;
  const lyricLines = [...lyricsEl.querySelectorAll('.lyric-line')];
  if (lyricLines.length) {
    const activeLine = Math.min(lyricLines.length - 1, Math.floor(media.currentTime / media.duration * lyricLines.length));
    lyricLines.forEach((line, index) => line.classList.toggle('active', index === activeLine));
  }
}
function onMediaEnded(media) {
  if (media !== activeMedia) return;
  playing = false;
  document.body.classList.remove('is-playing');
  playBtn.textContent = '\u25B6';
  playBtn.setAttribute('aria-label', 'Sing this rhyme');
  progressFill.style.width = '100%';
  lyricsEl.querySelectorAll('.lyric-line').forEach(line => line.classList.remove('active'));
}
function onMediaError(media) {
  if (media === activeMedia && currentRhyme?.audio_url) showToast('Could not load the music track. Check the audio file.');
}
[rhymeAudio, rhymeVideo].forEach(media => {
  media.addEventListener('play', onMediaPlay);
  media.addEventListener('timeupdate', () => onMediaTimeUpdate(media));
  media.addEventListener('ended', () => onMediaEnded(media));
  media.addEventListener('error', () => onMediaError(media));
});
cards.forEach((card, index) => card.addEventListener('click', () => selectCard(index)));
playBtn.addEventListener('click', speak);
musicToggle.addEventListener('click', toggleMusic);
document.getElementById('prevBtn').addEventListener('click', () => selectCard(activeIndex - 1));
document.getElementById('nextBtn').addEventListener('click', () => selectCard(activeIndex + 1));
favoriteBtn.addEventListener('click', () => {
  const saved = favoriteBtn.classList.toggle('active');
  favoriteBtn.textContent = saved ? '♥' : '♡';
  showToast(saved ? 'Added to your favorites!' : 'Removed from favorites');
});
selectCard(0);
