#!/usr/bin/env bash
# Chapter 10: a website build that sometimes fails, for the deploy script to use.
. /lab/setup/common.sh
fresh 10-scripts
rm -rf site build.sh live
mkdir -p site live
printf '<h1>Tara Observatory</h1>\n' > site/index.html
printf '<h1>Tonight in the sky</h1>\n' > site/tonight.html
cat > build.sh <<'SH'
#!/usr/bin/env bash
# Builds the site. Set BUILD_FAILS=1 to see what a failed build does.
if [ "${BUILD_FAILS:-0}" = 1 ]; then
  echo "build: error: tonight.html is not valid" >&2
  exit 1
fi
echo "build: 2 pages built"
SH
chmod +x build.sh
