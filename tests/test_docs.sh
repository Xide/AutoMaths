mkdocs serve --dev-addr 127.0.0.1:12354 --no-livereload &
sleep 1
while ! curl --output /dev/null --silent --head --fail http://127.0.0.1:12354
do
  sleep 0.2 && echo -n .
done
echo ''

# using --exclude-external here to prevent build fail due to
# timeout for network on shared runners
blc --exclude-external -rv http://127.0.0.1:12354
