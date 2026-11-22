# Shared by the chapter setups (they run as the learner): the learner's git identity, and commits with fixed
# authors and dates, so every learner gets the same history and the same commit hashes.
export HOME=/home/learner
cat > "$HOME/.gitconfig" <<'CFG'
[user]
	name = Learner
	email = learner@trails.example
[init]
	defaultBranch = main
[core]
	editor = nano
[pull]
	rebase = false
[advice]
	detachedHead = false
CFG
# who NAME: the next commits are by NAME (Asha, Ravi or Meera).
who() { export GIT_AUTHOR_NAME="$1" GIT_AUTHOR_EMAIL="$(echo "$1" | tr 'A-Z' 'a-z')@trails.example"
        export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"; }
who Asha
# commit DATE MESSAGE: commit what is staged, at a fixed date.
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }
# fresh FOLDER: start a chapter folder from nothing (a reset of the chapter).
fresh() { mkdir -p "/workspace/$1"; cd "/workspace/$1"; rm -rf trails server answer-*.txt; }
# The Trails website's first files.
trails_v1() {
  cat > README.md <<'MD'
# Trails

Treks in the Sahyadri hills near Pune and Mumbai, written by people who walked them.
MD
  cat > trails.md <<'MD'
# Trails

## Rajmachi
- Distance: 15 km
- Difficulty: easy
- Best season: June to September

## Kalsubai
- Distance: 6 km
- Difficulty: hard
- Best season: October to February
MD
}
