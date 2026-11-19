# Shared by the chapter setups (they run as the learner): the learner's git identity, and commits with fixed authors and dates
# so every learner gets the same history (and the same commit hashes).
export HOME=/home/learner
cat > "$HOME/.gitconfig" <<'CFG'
[user]
	name = Learner
	email = learner@labbox.local
[init]
	defaultBranch = main
[core]
	editor = nano
[pull]
	rebase = false
CFG
export GIT_AUTHOR_NAME=Kabir GIT_AUTHOR_EMAIL=kabir@brewpoint.example
export GIT_COMMITTER_NAME=Kabir GIT_COMMITTER_EMAIL=kabir@brewpoint.example
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }
